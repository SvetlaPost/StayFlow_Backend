from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj or request.user.is_staff

class IsSelfOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user and (request.user == obj or request.user.is_staff)