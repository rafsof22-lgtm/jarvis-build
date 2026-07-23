#!/usr/bin/env python3
"""Privacy-aware exact-message search over the local Jarvis reconstruction SQLite database."""
from __future__ import annotations
import argparse, sqlite3
from pathlib import Path

def search_index(db_path, keyword=None, project=None, category=None, date_range=None, role=None, code_only=False, limit=100, include_text=False):
    db_path=Path(db_path)
    if not db_path.exists() or db_path.stat().st_size==0: raise FileNotFoundError(f"Missing non-empty database: {db_path}")
    con=sqlite3.connect(db_path); con.row_factory=sqlite3.Row
    clauses=["1=1"]; params=[]
    if keyword: clauses.append("m.content_search LIKE ?"); params.append(f"%{keyword}%")
    if project: clauses.append("c.primary_project = ?"); params.append(project)
    if category: clauses.append("c.primary_category = ?"); params.append(category)
    if role: clauses.append("m.role = ?"); params.append(role)
    if code_only: clauses.append("m.code_density > 0")
    if date_range:
        start,end=date_range; clauses.append("c.created_at_utc >= ? AND c.created_at_utc <= ?"); params += [start,end]
    sql=f"""SELECT m.conversation_id,m.generated_message_id,m.generated_parent_id,m.message_seq,m.role,m.exact_sha256,m.source_pointer,m.word_count,m.char_count,m.code_density,m.syntax_markers,c.created_at_utc,c.created_at_melbourne,c.primary_project,c.primary_category,c.subcategory,c.jarvis_classification,c.confidence,c.deep_tags,CASE WHEN ? THEN m.content_search ELSE NULL END AS exact_text FROM messages m JOIN conversations c USING(conversation_id) WHERE {' AND '.join(clauses)} ORDER BY c.chronological_order,m.message_seq LIMIT ?"""
    rows=[dict(r) for r in con.execute(sql,[1 if include_text else 0,*params,int(limit)])]; con.close(); return rows

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--db',required=True); ap.add_argument('--keyword'); ap.add_argument('--project'); ap.add_argument('--category'); ap.add_argument('--role',choices=['user','assistant']); ap.add_argument('--code-only',action='store_true'); ap.add_argument('--include-text',action='store_true'); ap.add_argument('--limit',type=int,default=20); args=ap.parse_args()
    for row in search_index(args.db,args.keyword,args.project,args.category,None,args.role,args.code_only,args.limit,args.include_text): print(row)
if __name__=='__main__': main()
