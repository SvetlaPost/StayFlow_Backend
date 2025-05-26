from rest_framework import permissions


class IsBookingOwnerOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user == obj.renter or request.user.is_staff


class IsBookingRelatedOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user

        is_renter = obj.renter == user
        is_owner = obj.rent.owner == user
        is_admin = user.is_staff

        return is_renter or is_owner or is_admin
