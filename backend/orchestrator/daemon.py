import time
import os
from .auth import SentinelAuth
from .spatial_logic import detect_duplicates
from .resolver import ConflictResolver
from .audit import GovernanceAudit

class OrchestratorDaemon:
    """The central process that monitors the swarm and maintains system order."""
    
    def __init__(self):
        self.db = SentinelAuth.get_firestore()
        self.resolver = ConflictResolver()
        self.active_conflicts = set()

    def on_snapshot(self, col_snapshot, changes, read_time):
        """Callback for Firestore collection updates."""
        for change in changes:
            doc = change.document
            data = doc.to_dict()
            status = data.get('status')

            if change.type.name == 'ADDED' or change.type.name == 'MODIFIED':
                if status == 'triaged':
                    self.handle_triaged(doc, data)
                elif status == 'conflict':
                    self.handle_conflict(doc, data)

    def handle_triaged(self, doc, data):
        """Scans for spatial duplicates before promoting to awaiting_dispatch."""
        print(f"Checking for duplicates: {doc.id}")
        
        # Get all other triaged or dispatched events to check against
        existing = self.db.collection('emergencies')\
            .where('status', 'in', ['triaged', 'awaiting_dispatch', 'dispatched'])\
            .get()
        
        # Filter out current doc
        existing = [d for d in existing if d.id != doc.id]
        
        duplicate_id = detect_duplicates(data, existing)
        
        if duplicate_id:
            print(f"DUPLICATE DETECTED: {doc.id} merged into {duplicate_id}")
            doc.reference.update({
                "status": "merged",
                "merged_into": duplicate_id,
                "intelligence.meta_note": f"Merged into {duplicate_id} via Proxy User Logic."
            })
        else:
            print(f"PROMOTING: {doc.id} to awaiting_dispatch")
            doc.reference.update({"status": "awaiting_dispatch"})

    def handle_conflict(self, doc, data):
        """Invokes AI to resolve resource contention."""
        if doc.id in self.active_conflicts:
            return
            
        print(f"RESOLVING CONFLICT: {doc.id}")
        self.active_conflicts.add(doc.id)

        # Gather context: Available resources and other P1 emergencies
        resources = self.db.collection('resources').where('status', '==', 'available').get()
        resources_list = [r.to_dict() for r in resources]
        
        conflicts = [data] # Simplification: resolve this specific conflict doc
        
        resolution = self.resolver.resolve(conflicts, resources_list)
        
        if resolution and "decisions" in resolution:
            for decision in resolution["decisions"]:
                if decision["emergency_id"] == doc.id:
                    print(f"RESOLUTION FOUND: {decision['action']}")
                    doc.reference.update({
                        "status": "dispatched" if decision["action"] == "dispatch" else "awaiting_human_approval",
                        "resource_assignment.unit_id": decision.get("resource_id")
                    })
                    GovernanceAudit.log_audit(doc.id, decision["fairness_audit"])
                    
        self.active_conflicts.remove(doc.id)

    def run(self):
        """Starts the persistent listener."""
        print("SentinelMind Meta-Orchestrator Booted. Monitoring /emergencies...")
        query = self.db.collection('emergencies')
        watch = query.on_snapshot(self.on_snapshot)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down orchestrator...")
            watch.unsubscribe()

if __name__ == "__main__":
    daemon = OrchestratorDaemon()
    daemon.run()
