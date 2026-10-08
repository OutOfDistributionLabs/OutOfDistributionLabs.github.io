"""Deterministic retrieval controls and typed structural views; no model calls."""
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import time
from nltk.stem import PorterStemmer
from tree_sitter_languages import get_parser

LANG_EXT={'.py':'python','.cpp':'cpp','.cc':'cpp','.cxx':'cpp','.h':'cpp','.hpp':'cpp','.hh':'cpp','.c':'cpp','.java':'java','.ts':'typescript','.tsx':'tsx','.rs':'rust','.go':'go','.js':'javascript'}
FUNCTION_TYPES={'function_definition','method_declaration','constructor_declaration','function_declaration','function_item','method_declaration','method_definition','arrow_function'}
STOP=set('a an the this that these those and or of to in on at by for with from as is are be it its which what how function method returns return given provided input output implementation code does can will you'.split())
STEM=PorterStemmer()
@lru_cache(maxsize=200000)
def stem(t):return STEM.stem(t)
def tokens(text):
    text=re.sub(r'([a-z0-9])([A-Z])',r'\1 \2',text)
    text=re.sub(r'([A-Z])([A-Z][a-z])',r'\1 \2',text)
    return [stem(t) for t in re.findall(r'[a-zA-Z][a-zA-Z0-9]*',text.lower()) if t not in STOP and len(t)>1]
def safe_path(path):
    p=PurePosixPath(path)
    if p.is_absolute() or '..' in p.parts or not p.parts or '\\' in path:raise ValueError('Corpus paths must be safe relative paths')
    return p.as_posix()
def snapshot(content):
    h=hashlib.sha256()
    for p,text in sorted(content.items()):
        b=p.encode();h.update(len(b).to_bytes(8,'big'));h.update(b);b=text.encode();h.update(len(b).to_bytes(8,'big'));h.update(b)
    return 'sha256:'+h.hexdigest()
def read_workspace(root,max_bytes=100_000_000):
    root=Path(root).resolve();out={};size=0
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.suffix not in LANG_EXT or any(x in {'.git','node_modules','.venv','vendor','__pycache__'} for x in p.relative_to(root).parts):continue
        resolved=p.resolve()
        if not resolved.is_relative_to(root):raise ValueError('Symlink escapes task workspace')
        size+=p.stat().st_size
        if size>max_bytes:raise ValueError('Workspace corpus exceeds size budget')
        out[p.relative_to(root).as_posix()]=p.read_text(errors='replace')
    return out
@dataclass
class Entity:
    id:str
    path:str
    name:str
    start:int
    end:int
    code:str
    terms:Counter
    module:str

class Engine:
    def __init__(self,content,mode='graph',root=None):
        if mode not in {'scan','flat','graph'}:raise ValueError('Unknown mode')
        self.content={safe_path(p):t for p,t in content.items()};self.mode=mode;self.root=Path(root).resolve() if root else None
        self.snapshot_id=snapshot(self.content);self.entities=[];self.by_id={};self.file_members=defaultdict(list);self.module_members=defaultdict(list)
        self.links=defaultdict(set);self.signals=set();self.languages=set();self.parse_errors=0
        wall=time.perf_counter();cpu=time.process_time()
        for path,code in sorted(self.content.items()):self._extract(path,code)
        self.by_id={e.id:e for e in self.entities};self.df=Counter();self.postings=defaultdict(list)
        if self.mode!='scan':
            for i,e in enumerate(self.entities):
                for term,tf in e.terms.items():self.df[term]+=1;self.postings[term].append((i,tf))
        self.lengths=[sum(e.terms.values()) for e in self.entities];self.avgdl=sum(self.lengths)/max(1,len(self.lengths))
        if self.mode=='graph':
            names=defaultdict(list)
            for i,e in enumerate(self.entities):names[e.name].append(i)
            for i,e in enumerate(self.entities):
                for name in set(re.findall(r'\b([A-Za-z_]\w*)\s*\(',e.code)):
                    matches=[j for j in names[name] if self.entities[j].path==e.path and j!=i]
                    if len(matches)==1:self.links[i].add(matches[0]);self.links[matches[0]].add(i)
                    elif len(matches)>1:self.signals.add('ambiguous_symbol_calls')
            self.signals.add('call_edges_are_name_matching_hints_not_semantic_proofs')
        self.build_wall_ms=(time.perf_counter()-wall)*1000;self.build_cpu_ms=(time.process_time()-cpu)*1000
    def _extract(self,path,code):
        language=LANG_EXT.get(Path(path).suffix)
        if not language:self.signals.add('unsupported_language');return
        self.languages.add(language);raw=code.encode()
        try:tree=get_parser(language).parse(raw)
        except Exception:self.signals.add('unsupported_language');return
        if tree.root_node.has_error:self.parse_errors+=1;self.signals.add('parse_errors')
        stack=[tree.root_node]
        while stack:
            node=stack.pop();stack.extend(reversed(node.children))
            if node.type not in FUNCTION_TYPES:continue
            name_node=node.child_by_field_name('name')
            if name_node is None:
                declarator=node.child_by_field_name('declarator')
                if declarator is not None:
                    while declarator.child_by_field_name('declarator') is not None:declarator=declarator.child_by_field_name('declarator')
                    name_node=declarator
            name=raw[name_node.start_byte:name_node.end_byte].decode() if name_node else '<anonymous>'
            text=raw[node.start_byte:node.end_byte].decode();start=node.start_point[0]+1;end=node.end_point[0]+1
            eid=hashlib.sha256(f'{self.snapshot_id}:{path}:{node.start_byte}:{node.end_byte}'.encode()).hexdigest()
            module=str(PurePosixPath(path).parent)
            entity=Entity(eid,path,name,start,end,text,Counter(tokens(text+' '+path+' '+name)),module)
            i=len(self.entities);self.entities.append(entity);self.file_members[path].append(i);self.module_members[module].append(i)
    def status(self):
        return {'schema_version':'1','snapshot_id':self.snapshot_id,'mode':self.mode,'entity_count':len(self.entities),'languages':sorted(self.languages),'coverage_signals':sorted(self.signals),'parse_error_files':self.parse_errors,'engine_model_calls':0}
    def _stale(self,sid):return sid!=self.snapshot_id or (self.root is not None and snapshot(read_workspace(self.root))!=self.snapshot_id)
    def _scores(self,query):
        q=Counter(tokens(query));n=len(self.entities);scores=[0.0]*n
        if self.mode=='scan':
            for i,e in enumerate(self.entities):scores[i]=sum(min(e.terms.get(t,0),3) for t in q)/math.sqrt(max(1,self.lengths[i]))
            return scores
        for term in q:
            idf=math.log(1+(n-self.df[term]+.5)/(self.df[term]+.5))
            for i,tf in self.postings.get(term,[]):
                denom=tf+1.5*(1-.75+.75*self.lengths[i]/max(1,self.avgdl));scores[i]+=idf*tf*2.5/denom
        if self.mode=='flat':return scores
        top=max(scores,default=0)
        if top<=0:return scores
        base=[s/top for s in scores]
        # The abstraction views pool lexical support over file/module membership.
        f={p:sum(base[i] for i in ids)/len(ids) for p,ids in self.file_members.items()}
        m={p:sum(base[i] for i in ids)/len(ids) for p,ids in self.module_members.items()}
        return [.8*base[i]+.1*f[e.path]+.05*m[e.module]+.05*sum(base[j] for j in self.links[i])/max(1,len(self.links[i])) for i,e in enumerate(self.entities)]
    def query(self,snapshot_id,query,intent='locate',focus_ids=None,max_candidates=8,response_token_budget=2000):
        if intent not in {'locate','explain_dependency','suggest_tests','broaden'}:raise ValueError('Unknown intent')
        if not isinstance(max_candidates,int) or isinstance(max_candidates,bool) or not 1<=max_candidates<=50:raise ValueError('Candidate limit must be 1..50')
        if not isinstance(response_token_budget,int) or not 1024<=response_token_budget<=16000:raise ValueError('Response budget must be 1024..16000')
        if len(query)>20000:raise ValueError('Query exceeds input budget')
        wall=time.perf_counter();cpu=time.process_time()
        result={'schema_version':'1','snapshot_id':self.snapshot_id,'status':'ok','candidates':[],'coverage':{'signals':sorted(self.signals),'calibrated_probability':None},'recommended_action':'inspect','abstention_reason':None,'usage':{'index_cpu_ms':self.build_cpu_ms,'query_cpu_ms':0,'query_wall_ms':0,'response_bytes':0,'engine_model_input_tokens':0,'engine_model_output_tokens':0}}
        if self._stale(snapshot_id):result['status']='stale_snapshot';result['recommended_action']='reindex';result['abstention_reason']='Source revision changed or snapshot ID does not match.'
        elif not self.entities:result['status']='insufficient_evidence';result['abstention_reason']='No supported functions were extracted.'
        else:
            if any(i not in self.by_id for i in (focus_ids or [])):raise ValueError('Unknown or forged focus evidence ID')
            scores=self._scores(query);ranked=sorted(range(len(scores)),key=lambda i:(-scores[i],self.entities[i].path,self.entities[i].start))
            for i in ranked[:max_candidates]:
                if scores[i]<=0:continue
                e=self.entities[i];relation=[]
                if self.mode=='graph':
                    relation=[{'type':'contains','from':e.path,'to':e.id},{'type':'member_of_view','from':e.id,'to':e.module}]
                    if intent=='explain_dependency':relation += [{'type':'call_name_hint','from':e.id,'to':self.entities[j].id} for j in sorted(self.links[i])[:4]]
                result['candidates'].append({'entity_id':e.id,'path':e.path,'span':[e.start,e.end],'score':round(scores[i],6),'evidence_ids':[e.id],'reason':'BM25 and structural view support' if self.mode=='graph' else 'Lexical/symbol support','relation_path':relation})
            if not result['candidates']:result['status']='insufficient_evidence';result['recommended_action']='broaden';result['abstention_reason']='No lexical support found; inspect broader source or reformulate.'
            elif self.parse_errors:result['recommended_action']='inspect_and_broaden'
            if intent=='suggest_tests':result['coverage']['signals'].append('test_suggestions_are_source_retrieval_not_test_generation')
        result['usage']['query_cpu_ms']=(time.process_time()-cpu)*1000;result['usage']['query_wall_ms']=(time.perf_counter()-wall)*1000
        # Conservative UTF-8-byte budget: at most one token per byte; never claim an exact model tokenizer.
        limit=response_token_budget
        while result['candidates'] and len(json.dumps(result,ensure_ascii=False).encode())>limit:result['candidates'].pop()
        if not result['candidates'] and result['status']=='ok':result['status']='budget_exceeded';result['abstention_reason']='Response cannot fit conservative byte ceiling.'
        for _ in range(4):result['usage']['response_bytes']=len(json.dumps(result,ensure_ascii=False).encode())
        while len(json.dumps(result,ensure_ascii=False).encode())>limit and result['candidates']:result['candidates'].pop()
        if len(json.dumps(result,ensure_ascii=False).encode())>limit:
            result['coverage']['signals']=['coverage_detail_omitted_for_budget'];result['status']='budget_exceeded';result['candidates']=[]
        for _ in range(4):result['usage']['response_bytes']=len(json.dumps(result,ensure_ascii=False).encode())
        return result
    def evidence(self,snapshot_id,evidence_ids,response_token_budget=4000):
        if not isinstance(response_token_budget,int) or not 1024<=response_token_budget<=16000:raise ValueError('Evidence budget out of bounds')
        if len(evidence_ids)>50:raise ValueError('Too many evidence IDs')
        if self._stale(snapshot_id):return {'status':'stale_snapshot','evidence':[]}
        result={'status':'ok','snapshot_id':self.snapshot_id,'evidence':[]}
        for eid in evidence_ids:
            if eid not in self.by_id:raise ValueError('Unknown or forged evidence ID')
            e=self.by_id[eid];item={'entity_id':eid,'path':e.path,'span':[e.start,e.end],'source':e.code};result['evidence'].append(item)
            if len(json.dumps(result,ensure_ascii=False).encode())>response_token_budget:
                result['evidence'].pop();result['status']='budget_exceeded';break
        return result
