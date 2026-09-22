from fastapi import APIRouter

from app.modules.hr.api.v1.attendance_endpoints import router as attendance_router
from app.modules.hr.api.v1.employee_endpoints import router as employee_router
from app.modules.hr.api.v1.learning_endpoints import router as learning_router
from app.modules.hr.api.v1.leave_endpoints import router as leave_router
from app.modules.hr.api.v1.lifecycle_endpoints import router as lifecycle_router
from app.modules.hr.api.v1.payroll_endpoints import router as payroll_router
from app.modules.hr.api.v1.performance_endpoints import router as performance_router
from app.modules.hr.api.v1.profile_endpoints import router as profile_router
from app.modules.hr.api.v1.recruitment_endpoints import router as recruitment_router

router = APIRouter(prefix="/hr", tags=["Human Resources"])
router.include_router(employee_router)
router.include_router(profile_router)
router.include_router(lifecycle_router)
router.include_router(attendance_router)
router.include_router(leave_router)
router.include_router(payroll_router)
router.include_router(recruitment_router)
router.include_router(performance_router)
router.include_router(learning_router)
