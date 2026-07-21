from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path

from jarvis_health.synthetic_care_journeys_v17 import run_synthetic_care_journeys
from jarvis_business.cost_plus_profiles_v3 import (
    CostProfileStore, CustomerProfile, VehicleProfile, SupplierProfile, OrderProfile,
    WorkshopProfile, run_synthetic_order_to_billing, sha256_text,
)
from jarvis_staging.full_stack_digital_twin_v17 import FullStackDigitalTwinV17

ROOT=Path(__file__).resolve().parents[1]

class HealthJourneyTests(unittest.TestCase):
 def test_synthetic_care_journey(self):
  result=run_synthetic_care_journeys(':memory:')
  self.assertTrue(result['passed'])
  self.assertFalse(result['contains_direct_identifiers'])
  self.assertFalse(result['contains_raw_medical_values'])
  self.assertTrue(any(s['step']=='consent_withdrawal_blocks_new_diagnostic' and s['passed'] for s in result['steps']))

class CostProfileTests(unittest.TestCase):
 def test_profile_constraints_and_supplier_split(self):
  with tempfile.TemporaryDirectory() as td:
   store=CostProfileStore(Path(td)/'profiles.sqlite')
   c=CustomerProfile('c1','trade','ref://name','ref://contact','Clayton','captured','ACTIVE');store.upsert_customer(c)
   store.upsert_workshop(WorkshopProfile('w1','ref://w',sha256_text('abn'),('Clayton',),'APPROVED','policy://lead'))
   store.upsert_vehicle(VehicleProfile('v1','c1',sha256_text('vin'),sha256_text('rego'),'Toyota','Corolla',2020,'evidence://fitment'))
   store.upsert_supplier(SupplierProfile('s1','ref://s1','owner_supplied','API_SIMULATION','terms://s1'))
   store.upsert_supplier(SupplierProfile('s2','ref://s2','owner_supplied','API_SIMULATION','terms://s2'))
   store.create_order(OrderProfile('o1','c1','v1','trade','Clayton','r1',({'sku':'A','quantity':1,'supplier_id':'s1'},{'sku':'B','quantity':2,'supplier_id':'s2'}),'ACTIVE'))
   self.assertEqual(set(store.split_order_by_supplier('o1')),{'s1','s2'})
   self.assertEqual(store.counts(),{'customers':1,'workshops':1,'vehicles':1,'suppliers':2,'orders':1})
   store.close()

 def test_customer_direct_identifier_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   store=CostProfileStore(Path(td)/'profiles.sqlite')
   with self.assertRaisesRegex(ValueError,'pointer/reference'):
    store.upsert_customer(CustomerProfile('c1','trade','Real Name','person@example.com','Clayton','captured','ACTIVE'))
   store.close()

 def test_synthetic_order_to_billing(self):
  with tempfile.TemporaryDirectory() as td:
   result=run_synthetic_order_to_billing(Path(td)/'profiles.sqlite',Path(td)/'events.sqlite')
   self.assertTrue(result['passed'])
   self.assertEqual(result['supplier_split_count'],2)
   self.assertEqual(result['event_count'],3)
   self.assertFalse(result['provider_calls_executed'])

class FullStackTwinTests(unittest.TestCase):
 def twin(self,td,maximum_cost_aud=0):
  return FullStackDigitalTwinV17(ROOT/'registry/architecture/jarvis_full_stack_18_layer_reference_v1.json',Path(td)/'staging.sqlite',maximum_cost_aud=maximum_cost_aud)
 def test_runs_all_18_layers_and_retry(self):
  with tempfile.TemporaryDirectory() as td:
   twin=self.twin(td);result=twin.run(payload={'request_ref':'synthetic://v17'},transient_fail_layer='L08-WORKFLOW-EVENT-QUEUE')
   self.assertEqual(result['state'],'PASSED_LOCAL_SIMULATION');self.assertEqual(result['layer_count'],18)
   self.assertEqual(twin.persisted_layer_count(result['run_id']),18)
   self.assertEqual(result['retry_test'],'PASS');twin.close()
 def test_privacy_and_secret_gates(self):
  with tempfile.TemporaryDirectory() as td:
   twin=self.twin(td)
   with self.assertRaises(PermissionError):twin.run(payload={'email':'x@example.com'})
   with self.assertRaises(PermissionError):twin.run(payload={'api_key':'secret'})
   twin.close()
 def test_cost_ceiling(self):
  with tempfile.TemporaryDirectory() as td:
   twin=self.twin(td,maximum_cost_aud=0)
   with self.assertRaises(PermissionError):twin.run(payload={'request_ref':'x'},projected_cost_aud=0.01)
   twin.close()
 def test_backup_restore_and_rollback(self):
  with tempfile.TemporaryDirectory() as td:
   twin=self.twin(td);result=twin.run(payload={'request_ref':'synthetic://v17'})
   backup=twin.backup(Path(td)/'backup.sqlite');self.assertEqual(backup['state'],'BACKUP_CREATED')
   restore=twin.restore(Path(td)/'backup.sqlite',Path(td)/'restored.sqlite');self.assertEqual(restore['state'],'RESTORE_VERIFIED');self.assertEqual(restore['event_count'],18)
   rollback=twin.rollback(result['run_id']);self.assertEqual(rollback['remaining_layer_events'],0);self.assertFalse(rollback['external_side_effects']);twin.close()

class SourceRegistryTests(unittest.TestCase):
 def test_health_manifest_summary(self):
  data=json.loads((ROOT/'registry/health/health_claim_review_manifest_v17.json').read_text())
  self.assertEqual(data['conversation_count'],194);self.assertGreater(data['flag_occurrence_count'],0)
  self.assertRegex(data['overall_merkle_root'],r'^[0-9a-f]{64}$')
  self.assertNotIn('items',data)

class V17RegistryIntegrationTests(unittest.TestCase):
 def test_post_cutoff_archive_is_duplicate_not_fresh(self):
  data=json.loads((ROOT/'registry/source-accounting/post_2026_06_25_project_chat_delta_v17.json').read_text())
  self.assertEqual(data['comparison'],'EXACT_ARCHIVE_DUPLICATE')
  self.assertEqual(data['novel_export_bytes'],0)
  self.assertFalse(data['post_cutoff_delta_generated'])
  self.assertEqual(data['state'],'PENDING_INGEST')
 def test_remaining_six_projects_are_accounted_for(self):
  data=json.loads((ROOT/'registry/projects/remaining_requested_projects_reconstruction_v17.json').read_text())
  self.assertEqual({x['project_name'] for x in data['projects']},{'XRP Tracking New','Longevity Plan','Tax','Active Trust','Finance Planning','Financial New'})
 def test_local_staging_truth_boundary(self):
  data=json.loads((ROOT/'registry/staging/full_stack_local_staging_v17.json').read_text())
  self.assertEqual(data['layer_count'],18)
  self.assertFalse(data['connected_external_staging'])
  self.assertFalse(data['production_authorised'])
  self.assertEqual(data['projected_cost_aud'],0.0)
 def test_tracker_stays_open(self):
  data=json.loads((ROOT/'registry/trackers/all_progress_tracker_reconciliation_v17.json').read_text())
  self.assertEqual(data['program_state'],'ACTIVE_PROGRAM_NOT_100_PERCENT')
  self.assertEqual(data['current_states']['connected_external_staging'],'NOT_VERIFIED')
 def test_verifier_passes(self):
  import sys
  sys.path.insert(0,str(ROOT/'scripts'))
  from verify_completion_tranche_v17 import verify
  self.assertTrue(verify()['verified'])

if __name__=='__main__':unittest.main()
