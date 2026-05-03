from .models import ProjectMembership


def can_delete_task(task, user):
    if task.user_id == user.id:
        return True
    if not task.project_id:
        return False
    membership = ProjectMembership.objects.filter(project=task.project, user=user).first()
    return bool(
        membership
        and membership.role
        in {ProjectMembership.ROLE_OWNER, ProjectMembership.ROLE_EDITOR}
    )


def can_manage_collaborators(task, user):
    return task.user_id == user.id
