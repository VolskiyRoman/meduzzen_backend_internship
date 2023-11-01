from rest_framework import status
from rest_framework.test import APIClient

from .models import InvitationAction, InviteStatus, RequestAction, RequestStatus
from .test_fixtures import FixturesForAPITests


class InviteAPITestCase(FixturesForAPITests):
    def test_create_invite_good(self):
        client = self.user_login(self.user_1_payload)
        url = '/api/invite/'
        request_data = {"company": self.comp.id, "user": self.user2.id}
        response = client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invite_unauthorized(self):
        client = APIClient()
        url = '/api/invite/'
        request_data = {"company": self.comp.id, "user": self.user2.id}
        response = client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_invite_not_owner(self):
        client = self.user_login(self.user_2_payload)
        url = '/api/invite/'
        request_data = {"company": self.comp.id, "user": self.user2.id}
        response = client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_invite_already_in_company(self):
        client = self.user_login(self.user_1_payload)
        url = '/api/invite/'
        request_data = {"company": self.comp.id, "user": self.user1.id}
        response = client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invite_get(self):
        client = self.user_login(self.user_1_payload)
        url = '/api/invite/'
        request_data = {"company": self.comp.id, "user": self.user2.id}
        response = client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user2_invites = InvitationAction.objects.filter(user=self.user2).count()
        self.assertEqual(user2_invites, 1)

    def test_revoke_invitation(self):
        client = self.user_login(self.user_1_payload)
        url = '/api/invite/'
        request_data = {"company": self.comp.id, "user": self.user2.id}
        response = client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        invite_id = response.data.get('id')

        url = f'/api/invite/{invite_id}/revoke/'
        response = client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_decline_invitation(self):
        invite = InvitationAction.objects.create(company=self.comp, user=self.user2, status=InviteStatus.PENDING.value)

        client = self.user_login(self.user_2_payload)
        url = f'/api/invite/{invite.id}/decline/'
        response = client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_accept_invitation(self):
        invite = InvitationAction.objects.create(company=self.comp, user=self.user2, status=InviteStatus.PENDING.value)

        client = self.user_login(self.user_2_payload)
        url = f'/api/invite/{invite.id}/accept/'
        response = client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RequestAPITestCase(FixturesForAPITests):
    def test_create_request_good(self):
        client = self.user_login(self.user_2_payload)
        url = '/api/request/'
        request_data = {"company": self.comp.id, "user": self.user2.id}
        response = client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_request_unauthorized(self):
        client = APIClient()
        url = '/api/request/'
        request_data = {"company": self.comp.id, "user": self.user2.id}
        response = client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_request_already_in_company(self):
        client = self.user_login(self.user_1_payload)
        url = '/api/request/'
        request_data = {"company": self.comp.id, "user": self.user1.id}
        response = client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_request_get(self):
        client = self.user_login(self.user_1_payload)
        url = '/api/invite/'
        request_data = {"company": self.comp.id, "user": self.user2.id}
        response = client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user2_invites = InvitationAction.objects.filter(user=self.user2).count()

        self.user_login(self.user_2_payload)
        self.assertEqual(user2_invites, 1)

    def test_cancel_request(self):
        client = self.user_login(self.user_2_payload)
        url = '/api/request/'
        request_data = {"company": self.comp.id, "user": self.user2.id}
        response = client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        request_id = response.data.get('id')

        url = f'/api/request/{request_id}/cancel/'
        response = client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reject_request(self):
        request = RequestAction.objects.create(company=self.comp, user=self.user2, status=RequestStatus.PENDING.value)

        client = self.user_login(self.user_1_payload)
        url = f'/api/request/{request.id}/reject/'
        response = client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_approve_request(self):
        request = RequestAction.objects.create(company=self.comp, user=self.user2, status=RequestStatus.PENDING.value)

        client = self.user_login(self.user_1_payload)
        url = f'/api/request/{request.id}/approve/'
        response = client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CompanyAdminAPITestCase(FixturesForAPITests):
    def test_add_admin(self):
        self.comp.members.add(self.user2)

        client = self.user_login(self.user_1_payload)
        url = f'/api/companies/{self.comp.id}/add-admin/'
        request_data = {"user_id": self.user2.id}
        response = client.post(url, request_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_remove_admin(self):
        self.comp.members.add(self.user2)
        self.comp.admins.add(self.user2)

        client = self.user_login(self.user_1_payload)
        url = f'/api/companies/{self.comp.id}/remove-admin/'
        request_data = {"user_id": self.user2.id}
        response = client.post(url, request_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_admin_if_owner(self):
        self.comp.members.add(self.user1)

        client = self.user_login(self.user_1_payload)
        url = f'/api/companies/{self.comp.id}/add-admin/'
        request_data = {"user_id": self.user1.id}
        response = client.post(url, request_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_admin_bad(self):
        self.comp.members.add(self.user2)

        client = self.user_login(self.user_1_payload)
        url = f'/api/companies/{self.comp.id}/remove-admin/'
        request_data = {"user_id": self.user2.id}
        response = client.post(url, request_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

