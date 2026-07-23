import sqlite3, tempfile, unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from search_index import search_index

class SearchIndexTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.db=Path(self.tmp.name)/"t.sqlite"
        con=sqlite3.connect(self.db)
        con.executescript("""
        create table conversations(conversation_id text primary key, created_at_utc text, created_at_melbourne text,
          chronological_order integer, primary_project text, primary_category text, subcategory text,
          jarvis_classification text, confidence text, deep_tags text);
        create table messages(conversation_id text, generated_message_id text, generated_parent_id text,
          message_seq integer, role text, exact_sha256 text, source_pointer text, word_count integer,
          char_count integer, code_density real, syntax_markers text, content_search text);
        """)
        con.execute("insert into conversations values(?,?,?,?,?,?,?,?,?,?)",('c1','2026-01-01','2026-01-01',1,'02_Jarvis_Build_AI_Agents_Automation','Enterprise Architecture','Agents','Core Jarvis','Confirmed','jarvis'))
        con.execute("insert into messages values(?,?,?,?,?,?,?,?,?,?,?,?)",('c1','m1',None,1,'user','abc','p',3,12,0,'','build jarvis'))
        con.commit(); con.close()
    def tearDown(self): self.tmp.cleanup()
    def test_keyword_and_privacy_default(self):
        rows=search_index(self.db,keyword='jarvis')
        self.assertEqual(len(rows),1); self.assertIsNone(rows[0]['exact_text'])
    def test_include_text_local(self):
        rows=search_index(self.db,project='02_Jarvis_Build_AI_Agents_Automation',include_text=True)
        self.assertEqual(rows[0]['exact_text'],'build jarvis')
    def test_missing_db_fails(self):
        with self.assertRaises(FileNotFoundError): search_index(self.db.with_name('missing'))
if __name__=='__main__': unittest.main()
