import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user, get_scoped_db, require_role
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectOut

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_scoped_db),
    current_user: CurrentUser = Depends(require_role("admin", "member")),
):
    project = Project(id=uuid.uuid4(), tenant_id=current_user.tenant_id, name=payload.name)
    db.add(project)
    db.commit()
    return project


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_scoped_db), _: CurrentUser = Depends(get_current_user)):
    # No tenant_id filter here on purpose — RLS is what scopes this query.
    return db.execute(select(Project)).scalars().all()



@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_scoped_db),
    _: CurrentUser = Depends(get_current_user),
):
    # RLS hides other tenants' rows, so a foreign ID looks exactly like a missing one (404, not 403).
    project = db.execute(select(Project).where(Project.id == project_id)).scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_scoped_db),
    _: CurrentUser = Depends(require_role("admin")),
):
    project = db.execute(select(Project).where(Project.id == project_id)).scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)