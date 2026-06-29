"""API v1 router aggregation."""

from fastapi import APIRouter
from app.api.v1 import auth, users, materials, warehouses, inventory, receipts, issues, dashboard

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(materials.router, prefix="/materials", tags=["Materials"])
api_router.include_router(warehouses.router, prefix="/warehouses", tags=["Warehouses"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(receipts.router, prefix="/receipts", tags=["Receipts"])
api_router.include_router(issues.router, prefix="/issues", tags=["Issues"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
