"""Local read-only MCP over stdio; source workspace never includes grading assets."""
import argparse
from mcp.server.fastmcp import FastMCP
from .core import Engine, read_workspace

def make_server(engine):
    mcp=FastMCP('Out of Distribution Labs intuition engine')
    @mcp.tool()
    def intuition_status() -> dict:
        """Report snapshot, extraction coverage and engine capabilities; no correctness guarantee."""
        return engine.status()
    @mcp.tool()
    def intuition_query(snapshot_id:str,query:str,intent:str='locate',focus_ids:list[str]|None=None,max_candidates:int=8,response_token_budget:int=2000) -> dict:
        """Suggest source evidence to inspect next, grounded in the specified repository revision."""
        return engine.query(snapshot_id,query,intent,focus_ids,max_candidates,response_token_budget)
    @mcp.tool()
    def intuition_evidence(snapshot_id:str,evidence_ids:list[str],response_token_budget:int=4000) -> dict:
        """Read bounded source evidence for valid IDs; reject stale revisions and forged references."""
        return engine.evidence(snapshot_id,evidence_ids,response_token_budget)
    return mcp

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--mode',choices=['scan','flat','graph'],default='graph');a=p.parse_args()
    make_server(Engine(read_workspace(a.root),a.mode,root=a.root)).run(transport='stdio')
if __name__=='__main__':main()
