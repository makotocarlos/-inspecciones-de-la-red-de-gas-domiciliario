"""
Custom permissions for role-based access control
"""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission to only allow admin users
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'


class IsInspector(permissions.BasePermission):
    """
    Permission to only allow inspector users
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'INSPECTOR'


class IsAdminOrInspector(permissions.BasePermission):
    """
    Permission to allow admin or inspector users
    """
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                request.user.role in ['ADMIN', 'INSPECTOR'])


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to only allow owners of an object or admin users
    """
    def has_object_permission(self, request, view, obj):
        # Admin can access everything
        if request.user.role == 'ADMIN':
            return True
        
        # Check if object has user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if object is the user itself
        return obj == request.user


class IsOwnerOrInspectorOrAdmin(permissions.BasePermission):
    """
    Permission to allow owners, assigned inspectors, or admin users
    """
    def has_object_permission(self, request, view, obj):
        # Admin can access everything
        if request.user.role == 'ADMIN':
            return True
        
        # Inspector can access assigned inspections
        if request.user.role == 'INSPECTOR' and hasattr(obj, 'inspector'):
            return obj.inspector == request.user
        
        # Owner can access their own objects
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class ReadOnly(permissions.BasePermission):
    """
    Permission to only allow read-only access
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
