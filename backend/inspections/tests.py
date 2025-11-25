"""
Tests for Inspections app
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from inspections.models import Inspection, InspectionItem
from datetime import datetime, timedelta

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        email='admin@test.com',
        password='testpass123',
        first_name='Admin',
        last_name='Test',
        role=User.Role.ADMIN
    )


@pytest.fixture
def inspector_user(db):
    return User.objects.create_user(
        email='inspector@test.com',
        password='testpass123',
        first_name='Inspector',
        last_name='Test',
        role=User.Role.INSPECTOR,
        license_number='LIC-12345'
    )


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        email='user@test.com',
        password='testpass123',
        first_name='User',
        last_name='Test',
        role=User.Role.USER
    )


@pytest.fixture
def inspection(db, regular_user, inspector_user):
    return Inspection.objects.create(
        user=regular_user,
        inspector=inspector_user,
        address='Test Address 123',
        city='Test City',
        gas_type=Inspection.GasType.NATURAL,
        status=Inspection.Status.SCHEDULED,
        scheduled_date=datetime.now() + timedelta(days=1)
    )


@pytest.mark.django_db
class TestInspectionCreation:
    """Test inspection creation"""
    
    def test_user_can_create_inspection(self, api_client, regular_user):
        """Test that user can create inspection"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('inspection-list')
        data = {
            'address': 'Test Street 456',
            'city': 'Test City',
            'gas_type': Inspection.GasType.NATURAL,
            'installation_year': 2020
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['data']['address'] == 'Test Street 456'
        assert Inspection.objects.filter(address='Test Street 456').exists()
    
    def test_inspection_has_default_status(self, api_client, regular_user):
        """Test that new inspection has default status"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('inspection-list')
        data = {
            'address': 'Test Street 789',
            'city': 'Test City',
            'gas_type': Inspection.GasType.PROPANE
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['data']['status'] == Inspection.Status.PENDING


@pytest.mark.django_db
class TestInspectionPermissions:
    """Test inspection permissions"""
    
    def test_admin_can_view_all_inspections(self, api_client, admin_user, inspection):
        """Test that admin can view all inspections"""
        api_client.force_authenticate(user=admin_user)
        url = reverse('inspection-list')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']['results']) >= 1
    
    def test_inspector_can_view_assigned_inspections(self, api_client, inspector_user, inspection):
        """Test that inspector can view assigned inspections"""
        api_client.force_authenticate(user=inspector_user)
        url = reverse('inspection-list')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert any(i['id'] == str(inspection.id) for i in response.data['data']['results'])
    
    def test_user_can_only_view_own_inspections(self, api_client, regular_user, inspection):
        """Test that user can only view their own inspections"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('inspection-list')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert all(i['user']['id'] == str(regular_user.id) for i in response.data['data']['results'])
    
    def test_only_admin_can_assign_inspector(self, api_client, regular_user, inspection, inspector_user):
        """Test that only admin can assign inspector"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('inspection-assign-inspector', kwargs={'pk': inspection.id})
        data = {'inspector_id': str(inspector_user.id)}
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestInspectionWorkflow:
    """Test inspection workflow"""
    
    def test_admin_can_assign_inspector(self, api_client, admin_user, regular_user, inspector_user):
        """Test that admin can assign inspector to inspection"""
        # Create inspection without inspector
        inspection = Inspection.objects.create(
            user=regular_user,
            address='Test Address',
            city='Test City',
            gas_type=Inspection.GasType.NATURAL,
            status=Inspection.Status.PENDING
        )
        
        api_client.force_authenticate(user=admin_user)
        url = reverse('inspection-assign-inspector', kwargs={'pk': inspection.id})
        data = {'inspector_id': str(inspector_user.id)}
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        inspection.refresh_from_db()
        assert inspection.inspector == inspector_user
        assert inspection.status == Inspection.Status.SCHEDULED
    
    def test_inspector_can_complete_inspection(self, api_client, inspector_user, inspection):
        """Test that inspector can complete inspection"""
        inspection.status = Inspection.Status.IN_PROGRESS
        inspection.save()
        
        api_client.force_authenticate(user=inspector_user)
        url = reverse('inspection-complete', kwargs={'pk': inspection.id})
        data = {
            'result': Inspection.Result.APPROVED,
            'total_score': 85,
            'observations': 'All checks passed'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        inspection.refresh_from_db()
        assert inspection.status == Inspection.Status.COMPLETED
        assert inspection.result == Inspection.Result.APPROVED


@pytest.mark.django_db
class TestInspectionItems:
    """Test inspection items"""
    
    def test_create_inspection_item(self, inspection):
        """Test creating inspection item"""
        item = InspectionItem.objects.create(
            inspection=inspection,
            category='Gas Meter',
            item_name='Meter condition',
            is_compliant=True,
            score=9,
            observations='Good condition'
        )
        
        assert item.inspection == inspection
        assert item.is_compliant is True
        assert item.score == 9
    
    def test_inspection_items_ordering(self, inspection):
        """Test that inspection items are ordered correctly"""
        item1 = InspectionItem.objects.create(
            inspection=inspection,
            category='Test',
            item_name='Item 1',
            order=2
        )
        item2 = InspectionItem.objects.create(
            inspection=inspection,
            category='Test',
            item_name='Item 2',
            order=1
        )
        
        items = inspection.items.all()
        assert items[0] == item2
        assert items[1] == item1


@pytest.mark.django_db
class TestInspectionModel:
    """Test Inspection model"""
    
    def test_inspection_string_representation(self, inspection):
        """Test inspection __str__ method"""
        assert str(inspection).startswith('Inspección')
    
    def test_inspection_status_choices(self):
        """Test inspection status choices"""
        assert Inspection.Status.PENDING in dict(Inspection.Status.choices)
        assert Inspection.Status.SCHEDULED in dict(Inspection.Status.choices)
        assert Inspection.Status.COMPLETED in dict(Inspection.Status.choices)
