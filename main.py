from fastapi import FastAPI
from auth.auth_router import router as auth_router
from admin.workflows import router as workflow_router
from admin.trucks import router as truck_router
from admin.reports import router as report_router
from admin.users import router as user_router
from operator_routes.routes import router as operator_router  # ✅ NEW LINE
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Truck Management System API",
    description="Tracks truck entry, checkpoint progress, and admin workflows in a factory.",
    version="1.0.0"
)



# Configure this after creating `app`
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Admin routes
app.include_router(workflow_router, prefix="/workflows")
app.include_router(truck_router, prefix="/trucks")
app.include_router(user_router, prefix="/users")
app.include_router(report_router, prefix="/reports")

# ✅ Operator routes
app.include_router(operator_router, prefix="/operator")

# ✅ Auth routes
app.include_router(auth_router)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
