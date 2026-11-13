import uuid
import json
from fastapi import FastAPI, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from schemas import ApplicationRequest
from rules_engine import RulesEngine
from external_service import verify_background
import models
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Resilient Decision System",
    description="Configurable workflow decision platform for hackathon",
    version="1.0.0"
)

engine_rules = RulesEngine("config.json")
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "System is up and running!"}

@app.post("/api/v1/decisions")
def process_decision(
    request: ApplicationRequest, 
    idempotency_key: str = Header(..., description="Unique key to prevent duplicate processing"),
    db: Session = Depends(get_db)
):
    # 1. IDEMPOTENCY CHECK: Have we seen this key before?
    existing_request = db.query(models.RequestRecord).filter(models.RequestRecord.idempotency_key == idempotency_key).first()
    
    if existing_request:
        # Fetch the old audit log and return it immediately without reprocessing
        audit = existing_request.audit_log
        return {
            "message": "Duplicate request detected. Returning cached result.",
            "request_id": existing_request.id,
            "final_decision": existing_request.status,
            "rule_trace": json.loads(audit.trace) if audit else []
        }

    # 2. START NEW PROCESSING
    request_id = str(uuid.uuid4())
    data = request.model_dump()
    
    # Save as PENDING
    db_request = models.RequestRecord(
        id=request_id,
        idempotency_key=idempotency_key,
        applicant_name=data["applicant_name"],
        age=data["age"],
        income=data["income"],
        documents_provided=data["documents_provided"],
        status="PENDING"
    )
    db.add(db_request)
    db.commit()

    trace = []
    decision = ""

    # 3. EXTERNAL SERVICE CALL WITH FAILURES
    try:
        verify_background(data["applicant_name"])
        trace.append("External API Check: Passed background verification.")
        
        # 4. RULES EVALUATION (Only happens if external API succeeds)
        decision, rule_trace = engine_rules.evaluate(data)
        trace.extend(rule_trace) # Combine both traces
        
    except Exception as e:
        # If the external API fails completely after all retries
        decision = "FAILED"
        trace.append(f"External API Check: {str(e)}")

    # 5. UPDATE FINAL STATE AND AUDIT
    db_request.status = decision
    
    db_audit = models.AuditLog(
        request_id=request_id,
        decision=decision,
        trace=json.dumps(trace)
    )
    db.add(db_audit)
    db.commit()
    
    return {
        "request_id": request_id,
        "final_decision": decision,
        "rule_trace": trace
    }

@app.get("/api/v1/decisions/{request_id}/audit")
def get_audit_trail(request_id: str, db: Session = Depends(get_db)):
    audit = db.query(models.AuditLog).filter(models.AuditLog.request_id == request_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return {
        "request_id": audit.request_id,
        "decision": audit.decision,
        "trace": json.loads(audit.trace)
    }