"""
Outline API Client

This module provides a Python client for interacting with the Outline API.
"""

import json
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from .config import ConfigManager
from .exceptions import OutlineAPIError


class OutlineClient:
    """
    Client for interacting with Outline API.

    This client provides methods for all major Outline API operations including
    documents, collections, search, users, groups, comments, and attachments.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        """
        Initialize Outline API client.

        Args:
            api_key: Outline API key (format: ol_api_...). If not provided,
                    will try to load from environment or config file.
            base_url: Base URL for Outline API. Defaults to https://app.getoutline.com/api
            timeout: Request timeout in seconds.

        Raises:
            OutlineAPIError: If API key cannot be found or is invalid.
        """
        config = ConfigManager.load_config(require_api_key=False)
        config_api_key = config.get("api_key")
        config_base_url = config.get("base_url")
        config_timeout = config.get("timeout")

        self.api_key = api_key or (config_api_key if isinstance(config_api_key, str) else None)
        self.base_url = base_url or (
            config_base_url if isinstance(config_base_url, str) else ConfigManager.DEFAULT_BASE_URL
        )
        self.timeout = (
            timeout
            if timeout is not None
            else (config_timeout if isinstance(config_timeout, int) else ConfigManager.DEFAULT_TIMEOUT)
        )

        if not self.api_key:
            raise OutlineAPIError(
                "API key not found. Set OUTLINE_API_KEY environment variable or provide api_key parameter."
            )

        if not self.api_key.startswith("ol_api_"):
            raise OutlineAPIError("Invalid API key format. API key should start with 'ol_api_'")

    def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make HTTP request to Outline API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., 'documents.list')
            data: Request payload

        Returns:
            Response data as dictionary

        Raises:
            OutlineAPIError: If request fails
        """
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "outline-cli/0.1.0 (Python)",
        }

        request_data = json.dumps(data).encode("utf-8") if data else None

        try:
            req = urllib.request.Request(url, data=request_data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                response_data = json.loads(response.read().decode("utf-8"))
                if not isinstance(response_data, dict):
                    raise OutlineAPIError("Unexpected response format: expected a JSON object")
                return response_data
        except urllib.error.HTTPError as e:
            error_message = f"HTTP {e.code}: {e.reason}"
            try:
                error_data = json.loads(e.read().decode("utf-8"))
                if not isinstance(error_data, dict):
                    raise OutlineAPIError(error_message, status_code=e.code)
                error_message = error_data.get("message", error_message)
                raise OutlineAPIError(error_message, status_code=e.code, response=error_data)
            except json.JSONDecodeError:
                raise OutlineAPIError(error_message, status_code=e.code)
        except urllib.error.URLError as e:
            raise OutlineAPIError(f"Connection error: {e.reason}")
        except OutlineAPIError:
            raise
        except Exception as e:
            raise OutlineAPIError(f"Unexpected error: {e}")

    # Document Operations

    def documents_create(
        self,
        title: str,
        text: str,
        collection_id: str,
        parent_document_id: Optional[str] = None,
        template: bool = False,
        template_id: Optional[str] = None,
        publish: bool = True,
    ) -> Dict:
        """
        Create a new document.

        Args:
            title: Document title
            text: Document content in Markdown
            collection_id: ID of the collection to create document in
            parent_document_id: Optional parent document ID for nested documents
            template: Whether this is a template document
            template_id: Optional template ID to create from
            publish: Whether to publish immediately (default: True)

        Returns:
            Created document data

        Raises:
            OutlineAPIError: If creation fails
        """
        data = {
            "title": title,
            "text": text,
            "collectionId": collection_id,
            "publish": publish,
            "template": template,
        }
        if parent_document_id:
            data["parentDocumentId"] = parent_document_id
        if template_id:
            data["templateId"] = template_id

        return self._request("POST", "documents.create", data)

    def documents_info(self, id: str) -> Dict:
        """
        Get document information.

        Args:
            id: Document ID

        Returns:
            Document data

        Raises:
            OutlineAPIError: If request fails
        """
        return self._request("POST", "documents.info", {"id": id})

    def documents_list(self, collection_id: Optional[str] = None, limit: int = 25, offset: int = 0) -> Dict:
        """
        List documents.

        Args:
            collection_id: Optional collection ID to filter by
            limit: Number of documents to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of documents

        Raises:
            OutlineAPIError: If request fails
        """
        data: Dict[str, Any] = {"limit": limit, "offset": offset}
        if collection_id:
            data["collectionId"] = collection_id
        return self._request("POST", "documents.list", data)

    def documents_search(self, query: str, collection_id: Optional[str] = None, limit: int = 25) -> Dict:
        """
        Search documents by content.

        Args:
            query: Search query
            collection_id: Optional collection ID to limit search
            limit: Maximum number of results (default: 25)

        Returns:
            Search results

        Raises:
            OutlineAPIError: If request fails
        """
        data = {"query": query, "limit": limit}
        if collection_id:
            data["collectionId"] = collection_id
        return self._request("POST", "documents.search", data)

    def documents_search_titles(self, query: str, collection_id: Optional[str] = None, limit: int = 25) -> Dict:
        """
        Search documents by title only.

        Args:
            query: Search query
            collection_id: Optional collection ID to limit search
            limit: Maximum number of results (default: 25)

        Returns:
            Search results

        Raises:
            OutlineAPIError: If request fails
        """
        data = {"query": query, "limit": limit}
        if collection_id:
            data["collectionId"] = collection_id
        return self._request("POST", "documents.search_titles", data)

    def documents_update(
        self,
        id: str,
        title: Optional[str] = None,
        text: Optional[str] = None,
        publish: Optional[bool] = None,
    ) -> Dict:
        """
        Update a document.

        Args:
            id: Document ID
            title: New title (optional)
            text: New content (optional)
            publish: Publish status (optional)

        Returns:
            Updated document data

        Raises:
            OutlineAPIError: If update fails
        """
        data: Dict[str, Any] = {"id": id}
        if title is not None:
            data["title"] = title
        if text is not None:
            data["text"] = text
        if publish is not None:
            data["publish"] = publish
        return self._request("POST", "documents.update", data)

    def documents_delete(self, id: str, permanent: bool = False) -> Dict:
        """
        Delete a document.

        Args:
            id: Document ID
            permanent: Whether to permanently delete (default: False, archives instead)

        Returns:
            Deletion confirmation

        Raises:
            OutlineAPIError: If deletion fails
        """
        return self._request("POST", "documents.delete", {"id": id, "permanent": permanent})

    def documents_archive(self, id: str) -> Dict:
        """
        Archive a document.

        Args:
            id: Document ID

        Returns:
            Archived document data

        Raises:
            OutlineAPIError: If archiving fails
        """
        return self._request("POST", "documents.archive", {"id": id})

    def documents_restore(self, id: str) -> Dict:
        """
        Restore an archived document.

        Args:
            id: Document ID

        Returns:
            Restored document data

        Raises:
            OutlineAPIError: If restoration fails
        """
        return self._request("POST", "documents.restore", {"id": id})

    def documents_move(
        self,
        id: str,
        collection_id: Optional[str] = None,
        parent_document_id: Optional[str] = None,
    ) -> Dict:
        """
        Move a document to a different collection or parent.

        Args:
            id: Document ID
            collection_id: Optional new collection ID
            parent_document_id: Optional new parent document ID

        Returns:
            Moved document data

        Raises:
            OutlineAPIError: If move fails
        """
        data = {"id": id}
        if collection_id:
            data["collectionId"] = collection_id
        if parent_document_id:
            data["parentDocumentId"] = parent_document_id
        return self._request("POST", "documents.move", data)

    def documents_duplicate(
        self,
        id: str,
        title: Optional[str] = None,
        collection_id: Optional[str] = None,
        parent_document_id: Optional[str] = None,
        publish: bool = False,
    ) -> Dict:
        """
        Duplicate a document.

        Args:
            id: Document ID to duplicate
            title: Optional title for the duplicate
            collection_id: Optional collection ID for the duplicate
            parent_document_id: Optional parent document ID
            publish: Whether to publish the duplicate (default: False)

        Returns:
            Duplicated document data

        Raises:
            OutlineAPIError: If duplication fails
        """
        data = {"id": id, "publish": publish}
        if title:
            data["title"] = title
        if collection_id:
            data["collectionId"] = collection_id
        if parent_document_id:
            data["parentDocumentId"] = parent_document_id
        return self._request("POST", "documents.duplicate", data)

    def documents_templatize(self, id: str) -> Dict:
        """
        Convert a document to a template.

        Args:
            id: Document ID

        Returns:
            Template document data

        Raises:
            OutlineAPIError: If conversion fails
        """
        return self._request("POST", "documents.templatize", {"id": id})

    def documents_export(self, id: str) -> Dict:
        """
        Export a document as Markdown.

        Args:
            id: Document ID

        Returns:
            Document export data

        Raises:
            OutlineAPIError: If export fails
        """
        return self._request("POST", "documents.export", {"id": id})

    def documents_import(
        self,
        file: str,
        collection_id: str,
        parent_document_id: Optional[str] = None,
        publish: bool = True,
    ) -> Dict:
        """
        Import a document from a file.

        Args:
            file: File content or path
            collection_id: Collection ID to import into
            parent_document_id: Optional parent document ID
            publish: Whether to publish immediately (default: True)

        Returns:
            Imported document data

        Raises:
            OutlineAPIError: If import fails
        """
        data: Dict[str, Any] = {
            "file": file,
            "collectionId": collection_id,
            "publish": publish,
        }
        if parent_document_id:
            data["parentDocumentId"] = parent_document_id
        return self._request("POST", "documents.import", data)

    def documents_drafts(self, collection_id: Optional[str] = None, limit: int = 25, offset: int = 0) -> Dict:
        """
        List draft documents.

        Args:
            collection_id: Optional collection ID to filter by
            limit: Number of documents to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of draft documents

        Raises:
            OutlineAPIError: If request fails
        """
        data: Dict[str, Any] = {"limit": limit, "offset": offset}
        if collection_id:
            data["collectionId"] = collection_id
        return self._request("POST", "documents.drafts", data)

    def documents_archived(self, limit: int = 25, offset: int = 0) -> Dict:
        """
        List archived documents.

        Args:
            limit: Number of documents to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of archived documents

        Raises:
            OutlineAPIError: If request fails
        """
        return self._request("POST", "documents.archived", {"limit": limit, "offset": offset})

    def documents_deleted(self, limit: int = 25, offset: int = 0) -> Dict:
        """
        List deleted documents.

        Args:
            limit: Number of documents to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of deleted documents

        Raises:
            OutlineAPIError: If request fails
        """
        return self._request("POST", "documents.deleted", {"limit": limit, "offset": offset})

    def documents_viewed(self, limit: int = 25, offset: int = 0) -> Dict:
        """
        List recently viewed documents.

        Args:
            limit: Number of documents to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of recently viewed documents

        Raises:
            OutlineAPIError: If request fails
        """
        return self._request("POST", "documents.viewed", {"limit": limit, "offset": offset})

    def documents_documents(self, limit: int = 25, offset: int = 0) -> Dict:
        """
        List all documents (alternative to documents.list).

        Args:
            limit: Number of documents to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of documents

        Raises:
            OutlineAPIError: If request fails
        """
        return self._request("POST", "documents.documents", {"limit": limit, "offset": offset})

    def documents_empty_trash(self) -> Dict:
        """
        Empty the trash (permanently delete all deleted documents).

        Returns:
            Confirmation data

        Raises:
            OutlineAPIError: If operation fails
        """
        return self._request("POST", "documents.empty_trash", {})

    def documents_unpublish(self, id: str) -> Dict:
        """
        Unpublish a document (convert to draft).

        Args:
            id: Document ID

        Returns:
            Unpublished document data

        Raises:
            OutlineAPIError: If operation fails
        """
        return self._request("POST", "documents.unpublish", {"id": id})

    def documents_add_user(self, id: str, user_id: str, permission: str = "read") -> Dict:
        """
        Add a user to a document with specific permissions.

        Args:
            id: Document ID
            user_id: User ID to add
            permission: Permission level ('read' or 'read_write', default: 'read')

        Returns:
            Membership data

        Raises:
            OutlineAPIError: If operation fails
        """
        return self._request(
            "POST",
            "documents.add_user",
            {
                "id": id,
                "userId": user_id,
                "permission": permission,
            },
        )

    def documents_remove_user(self, id: str, user_id: str) -> Dict:
        """
        Remove a user from a document.

        Args:
            id: Document ID
            user_id: User ID to remove

        Returns:
            Confirmation data

        Raises:
            OutlineAPIError: If operation fails
        """
        return self._request(
            "POST",
            "documents.remove_user",
            {
                "id": id,
                "userId": user_id,
            },
        )

    def documents_memberships(self, id: str, query: Optional[str] = None, limit: int = 25, offset: int = 0) -> Dict:
        """
        List user memberships for a document.

        Args:
            id: Document ID
            query: Optional search query to filter users
            limit: Number of memberships to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of user memberships

        Raises:
            OutlineAPIError: If request fails
        """
        data: Dict[str, Any] = {"id": id, "limit": limit, "offset": offset}
        if query:
            data["query"] = query
        return self._request("POST", "documents.memberships", data)

    def documents_users(self, id: str, query: Optional[str] = None, limit: int = 25, offset: int = 0) -> Dict:
        """
        List users with access to a document.

        Args:
            id: Document ID
            query: Optional search query to filter users
            limit: Number of users to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of users

        Raises:
            OutlineAPIError: If request fails
        """
        data: Dict[str, Any] = {"id": id, "limit": limit, "offset": offset}
        if query:
            data["query"] = query
        return self._request("POST", "documents.users", data)

    def documents_add_group(self, id: str, group_id: str, permission: str = "read") -> Dict:
        """
        Add a group to a document with specific permissions.

        Args:
            id: Document ID
            group_id: Group ID to add
            permission: Permission level ('read' or 'read_write', default: 'read')

        Returns:
            Membership data

        Raises:
            OutlineAPIError: If operation fails
        """
        return self._request(
            "POST",
            "documents.add_group",
            {
                "id": id,
                "groupId": group_id,
                "permission": permission,
            },
        )

    def documents_remove_group(self, id: str, group_id: str) -> Dict:
        """
        Remove a group from a document.

        Args:
            id: Document ID
            group_id: Group ID to remove

        Returns:
            Confirmation data

        Raises:
            OutlineAPIError: If operation fails
        """
        return self._request(
            "POST",
            "documents.remove_group",
            {
                "id": id,
                "groupId": group_id,
            },
        )

    def documents_group_memberships(
        self, id: str, query: Optional[str] = None, limit: int = 25, offset: int = 0
    ) -> Dict:
        """
        List group memberships for a document.

        Args:
            id: Document ID
            query: Optional search query to filter groups
            limit: Number of memberships to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of group memberships

        Raises:
            OutlineAPIError: If request fails
        """
        data: Dict[str, Any] = {"id": id, "limit": limit, "offset": offset}
        if query:
            data["query"] = query
        return self._request("POST", "documents.group_memberships", data)

    # Collection Operations

    def collections_list(self, limit: int = 25, offset: int = 0) -> Dict:
        """
        List all collections.

        Args:
            limit: Number of collections to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of collections

        Raises:
            OutlineAPIError: If request fails
        """
        return self._request("POST", "collections.list", {"limit": limit, "offset": offset})

    def collections_info(self, id: str) -> Dict:
        """
        Get collection information.

        Args:
            id: Collection ID

        Returns:
            Collection data

        Raises:
            OutlineAPIError: If request fails
        """
        return self._request("POST", "collections.info", {"id": id})

    def collections_create(self, name: str, description: Optional[str] = None, color: Optional[str] = None) -> Dict:
        """
        Create a new collection.

        Args:
            name: Collection name
            description: Optional description
            color: Optional color (hex format)

        Returns:
            Created collection data

        Raises:
            OutlineAPIError: If creation fails
        """
        data = {"name": name}
        if description:
            data["description"] = description
        if color:
            data["color"] = color
        return self._request("POST", "collections.create", data)

    def collections_update(
        self,
        id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[str] = None,
    ) -> Dict:
        """
        Update a collection.

        Args:
            id: Collection ID
            name: New name (optional)
            description: New description (optional)
            color: New color (optional)

        Returns:
            Updated collection data

        Raises:
            OutlineAPIError: If update fails
        """
        data = {"id": id}
        if name:
            data["name"] = name
        if description:
            data["description"] = description
        if color:
            data["color"] = color
        return self._request("POST", "collections.update", data)

    def collections_delete(self, id: str) -> Dict:
        """
        Delete a collection.

        Args:
            id: Collection ID

        Returns:
            Deletion confirmation

        Raises:
            OutlineAPIError: If deletion fails
        """
        return self._request("POST", "collections.delete", {"id": id})

    def collections_documents(self, id: str, limit: int = 25, offset: int = 0) -> Dict:
        """
        List documents in a collection.

        Args:
            id: Collection ID
            limit: Number of documents to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of documents

        Raises:
            OutlineAPIError: If request fails
        """
        return self._request(
            "POST",
            "collections.documents",
            {
                "id": id,
                "limit": limit,
                "offset": offset,
            },
        )

    def collections_add_user(self, id: str, user_id: str, permission: str = "read") -> Dict:
        """
        Add a user to a collection with specific permissions.

        Args:
            id: Collection ID
            user_id: User ID to add
            permission: Permission level ('read', 'read_write', or 'admin', default: 'read')

        Returns:
            Membership data

        Raises:
            OutlineAPIError: If operation fails
        """
        return self._request(
            "POST",
            "collections.add_user",
            {
                "id": id,
                "userId": user_id,
                "permission": permission,
            },
        )

    def collections_remove_user(self, id: str, user_id: str) -> Dict:
        """
        Remove a user from a collection.

        Args:
            id: Collection ID
            user_id: User ID to remove

        Returns:
            Confirmation data

        Raises:
            OutlineAPIError: If operation fails
        """
        return self._request(
            "POST",
            "collections.remove_user",
            {
                "id": id,
                "userId": user_id,
            },
        )

    def collections_memberships(self, id: str, query: Optional[str] = None, limit: int = 25, offset: int = 0) -> Dict:
        """
        List user memberships for a collection.

        Args:
            id: Collection ID
            query: Optional search query to filter users
            limit: Number of memberships to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of user memberships

        Raises:
            OutlineAPIError: If request fails
        """
        data: Dict[str, Any] = {"id": id, "limit": limit, "offset": offset}
        if query:
            data["query"] = query
        return self._request("POST", "collections.memberships", data)

    def collections_add_group(self, id: str, group_id: str, permission: str = "read") -> Dict:
        """
        Add a group to a collection with specific permissions.

        Args:
            id: Collection ID
            group_id: Group ID to add
            permission: Permission level ('read', 'read_write', or 'admin', default: 'read')

        Returns:
            Membership data

        Raises:
            OutlineAPIError: If operation fails
        """
        return self._request(
            "POST",
            "collections.add_group",
            {
                "id": id,
                "groupId": group_id,
                "permission": permission,
            },
        )

    def collections_remove_group(self, id: str, group_id: str) -> Dict:
        """
        Remove a group from a collection.

        Args:
            id: Collection ID
            group_id: Group ID to remove

        Returns:
            Confirmation data

        Raises:
            OutlineAPIError: If operation fails
        """
        return self._request(
            "POST",
            "collections.remove_group",
            {
                "id": id,
                "groupId": group_id,
            },
        )

    def collections_group_memberships(
        self, id: str, query: Optional[str] = None, limit: int = 25, offset: int = 0
    ) -> Dict:
        """
        List group memberships for a collection.

        Args:
            id: Collection ID
            query: Optional search query to filter groups
            limit: Number of memberships to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of group memberships

        Raises:
            OutlineAPIError: If request fails
        """
        data: Dict[str, Any] = {"id": id, "limit": limit, "offset": offset}
        if query:
            data["query"] = query
        return self._request("POST", "collections.group_memberships", data)

    def collections_export(self, id: str, format: str = "outline-markdown") -> Dict:
        """
        Export a collection.

        Args:
            id: Collection ID
            format: Export format (default: 'outline-markdown')

        Returns:
            Export data with download URL

        Raises:
            OutlineAPIError: If export fails
        """
        return self._request(
            "POST",
            "collections.export",
            {
                "id": id,
                "format": format,
            },
        )

    def collections_export_all(self, format: str = "outline-markdown") -> Dict:
        """
        Export all collections.

        Args:
            format: Export format (default: 'outline-markdown')

        Returns:
            Export data with download URL

        Raises:
            OutlineAPIError: If export fails
        """
        return self._request(
            "POST",
            "collections.export_all",
            {
                "format": format,
            },
        )

    # User Operations

    def users_list(self, limit: int = 25, offset: int = 0, query: Optional[str] = None) -> Dict:
        """
        List all users in the workspace.

        Args:
            limit: Number of users to return (default: 25)
            offset: Pagination offset (default: 0)
            query: Optional search query to filter users

        Returns:
            List of users

        Raises:
            OutlineAPIError: If request fails
        """
        data: Dict[str, Any] = {"limit": limit, "offset": offset}
        if query:
            data["query"] = query
        return self._request("POST", "users.list", data)

    def users_info(self, id: str) -> Dict:
        """
        Get user information.

        Args:
            id: User ID

        Returns:
            User data

        Raises:
            OutlineAPIError: If request fails
        """
        return self._request("POST", "users.info", {"id": id})

    def users_invite(self, email: str, name: Optional[str] = None, role: str = "member") -> Dict:
        """
        Invite a new user to the workspace.

        Args:
            email: User email address
            name: Optional user name
            role: User role ('member', 'viewer', or 'admin', default: 'member')

        Returns:
            Invited user data

        Raises:
            OutlineAPIError: If invitation fails
        """
        data: Dict[str, Any] = {"email": email, "role": role}
        if name:
            data["name"] = name
        return self._request("POST", "users.invite", data)

    def users_update(self, id: str, name: Optional[str] = None, avatar_url: Optional[str] = None) -> Dict:
        """
        Update user information.

        Args:
            id: User ID
            name: New name (optional)
            avatar_url: New avatar URL (optional)

        Returns:
            Updated user data

        Raises:
            OutlineAPIError: If update fails
        """
        data: Dict[str, Any] = {"id": id}
        if name:
            data["name"] = name
        if avatar_url:
            data["avatarUrl"] = avatar_url
        return self._request("POST", "users.update", data)

    def users_update_role(self, id: str, role: str) -> Dict:
        """
        Update user role.

        Args:
            id: User ID
            role: New role ('member', 'viewer', or 'admin')

        Returns:
            Updated user data

        Raises:
            OutlineAPIError: If update fails
        """
        return self._request(
            "POST",
            "users.update_role",
            {
                "id": id,
                "role": role,
            },
        )

    def users_suspend(self, id: str) -> Dict:
        """
        Suspend a user.

        Args:
            id: User ID

        Returns:
            Suspended user data

        Raises:
            OutlineAPIError: If suspension fails
        """
        return self._request("POST", "users.suspend", {"id": id})

    def users_activate(self, id: str) -> Dict:
        """
        Activate a suspended user.

        Args:
            id: User ID

        Returns:
            Activated user data

        Raises:
            OutlineAPIError: If activation fails
        """
        return self._request("POST", "users.activate", {"id": id})

    def users_delete(self, id: str) -> Dict:
        """
        Delete a user.

        Args:
            id: User ID

        Returns:
            Deletion confirmation

        Raises:
            OutlineAPIError: If deletion fails
        """
        return self._request("POST", "users.delete", {"id": id})

    # Group Operations

    def groups_list(self, limit: int = 25, offset: int = 0) -> Dict:
        """
        List all groups in the workspace.

        Args:
            limit: Number of groups to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of groups

        Raises:
            OutlineAPIError: If request fails
        """
        return self._request("POST", "groups.list", {"limit": limit, "offset": offset})

    def groups_info(self, id: str) -> Dict:
        """
        Get group information.

        Args:
            id: Group ID

        Returns:
            Group data

        Raises:
            OutlineAPIError: If request fails
        """
        return self._request("POST", "groups.info", {"id": id})

    def groups_create(self, name: str) -> Dict:
        """
        Create a new group.

        Args:
            name: Group name

        Returns:
            Created group data

        Raises:
            OutlineAPIError: If creation fails
        """
        return self._request("POST", "groups.create", {"name": name})

    def groups_update(self, id: str, name: str) -> Dict:
        """
        Update a group.

        Args:
            id: Group ID
            name: New group name

        Returns:
            Updated group data

        Raises:
            OutlineAPIError: If update fails
        """
        return self._request("POST", "groups.update", {"id": id, "name": name})

    def groups_delete(self, id: str) -> Dict:
        """
        Delete a group.

        Args:
            id: Group ID

        Returns:
            Deletion confirmation

        Raises:
            OutlineAPIError: If deletion fails
        """
        return self._request("POST", "groups.delete", {"id": id})

    def groups_add_user(self, id: str, user_id: str) -> Dict:
        """
        Add a user to a group.

        Args:
            id: Group ID
            user_id: User ID to add

        Returns:
            Membership data

        Raises:
            OutlineAPIError: If operation fails
        """
        return self._request(
            "POST",
            "groups.add_user",
            {
                "id": id,
                "userId": user_id,
            },
        )

    def groups_remove_user(self, id: str, user_id: str) -> Dict:
        """
        Remove a user from a group.

        Args:
            id: Group ID
            user_id: User ID to remove

        Returns:
            Confirmation data

        Raises:
            OutlineAPIError: If operation fails
        """
        return self._request(
            "POST",
            "groups.remove_user",
            {
                "id": id,
                "userId": user_id,
            },
        )

    def groups_memberships(self, id: str, query: Optional[str] = None, limit: int = 25, offset: int = 0) -> Dict:
        """
        List user memberships for a group.

        Args:
            id: Group ID
            query: Optional search query to filter users
            limit: Number of memberships to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of user memberships

        Raises:
            OutlineAPIError: If request fails
        """
        data: Dict[str, Any] = {"id": id, "limit": limit, "offset": offset}
        if query:
            data["query"] = query
        return self._request("POST", "groups.memberships", data)

    # File Operations

    def file_operations_list(self, type: str = "export", limit: int = 25, offset: int = 0) -> Dict:
        """
        List file operations.

        Args:
            type: Operation type filter ('import' or 'export', default: 'export')
            limit: Number of operations to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of file operations

        Raises:
            OutlineAPIError: If request fails
        """
        data: Dict[str, Any] = {"type": type, "limit": limit, "offset": offset}
        return self._request("POST", "fileOperations.list", data)

    def file_operations_info(self, id: str) -> Dict:
        """
        Get file operation information.

        Args:
            id: File operation ID

        Returns:
            File operation data

        Raises:
            OutlineAPIError: If request fails
        """
        return self._request("POST", "fileOperations.info", {"id": id})

    def file_operations_redirect(self, id: str) -> Dict:
        """
        Get redirect URL for a file operation download.

        Args:
            id: File operation ID

        Returns:
            Dict with 'url' key containing the redirect URL

        Raises:
            OutlineAPIError: If request fails
        """
        # This endpoint returns a 302 redirect, not JSON
        data = json.dumps({"id": id}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/fileOperations.redirect",
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "outline-cli/0.1.0",
            },
            method="POST",
        )

        try:
            # Don't follow redirects automatically
            class NoRedirect(urllib.request.HTTPRedirectHandler):
                def redirect_request(self, req, fp, code, msg, headers, newurl):
                    return None

            opener = urllib.request.build_opener(NoRedirect)
            opener.open(req, timeout=self.timeout)
            # If we get here without redirect, something is wrong
            raise OutlineAPIError("Expected redirect but got normal response")
        except urllib.error.HTTPError as e:
            if e.code in [301, 302, 303, 307, 308]:
                # This is the expected redirect
                redirect_url = e.headers.get("Location")
                if redirect_url:
                    return {
                        "url": redirect_url,
                        "status": e.code,
                        "ok": True,
                    }
                else:
                    raise OutlineAPIError("Redirect response missing Location header")
            else:
                # This is an actual error
                try:
                    error_data = json.loads(e.read().decode("utf-8"))
                    error_message = error_data.get("message", str(e))
                except Exception:
                    error_message = str(e)
                raise OutlineAPIError(f"[HTTP {e.code}] {error_message}", status_code=e.code)

    def file_operations_delete(self, id: str) -> Dict:
        """
        Delete a file operation.

        Args:
            id: File operation ID

        Returns:
            Deletion confirmation

        Raises:
            OutlineAPIError: If deletion fails
        """
        return self._request("POST", "fileOperations.delete", {"id": id})

    # Comment Operations

    def comments_create(self, document_id: str, data: Dict, parent_comment_id: Optional[str] = None) -> Dict:
        """
        Create a new comment on a document.

        Args:
            document_id: Document ID to comment on
            data: Comment content in ProseMirror JSON format
            parent_comment_id: Optional parent comment ID for replies

        Returns:
            Created comment data

        Raises:
            OutlineAPIError: If creation fails
        """
        payload = {"documentId": document_id, "data": data}
        if parent_comment_id:
            payload["parentCommentId"] = parent_comment_id
        return self._request("POST", "comments.create", payload)

    def comments_list(self, document_id: str, limit: int = 25, offset: int = 0) -> Dict:
        """
        List comments on a document.

        Args:
            document_id: Document ID
            limit: Number of comments to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of comments

        Raises:
            OutlineAPIError: If request fails
        """
        return self._request("POST", "comments.list", {"documentId": document_id, "limit": limit, "offset": offset})

    def comments_info(self, id: str) -> Dict:
        """
        Get comment information.

        Args:
            id: Comment ID

        Returns:
            Comment data

        Raises:
            OutlineAPIError: If request fails
        """
        return self._request("POST", "comments.info", {"id": id})

    def comments_update(self, id: str, data: Dict) -> Dict:
        """
        Update a comment.

        Args:
            id: Comment ID
            data: New comment content in ProseMirror JSON format

        Returns:
            Updated comment data

        Raises:
            OutlineAPIError: If update fails
        """
        return self._request("POST", "comments.update", {"id": id, "data": data})

    def comments_delete(self, id: str) -> Dict:
        """
        Delete a comment.

        Args:
            id: Comment ID

        Returns:
            Deletion confirmation

        Raises:
            OutlineAPIError: If deletion fails
        """
        return self._request("POST", "comments.delete", {"id": id})

    # Attachment Operations

    def attachments_create(
        self,
        name: str,
        document_id: str,
        content_type: str,
        size: int,
        preset: str = "documentAttachment",
    ) -> Dict:
        """
        Create an attachment and get upload URL.

        Args:
            name: Attachment filename
            document_id: Document ID to attach to
            content_type: MIME type (e.g., 'image/png', 'application/pdf')
            size: File size in bytes
            preset: Upload preset (default: 'documentAttachment')

        Returns:
            Attachment data with upload URL

        Raises:
            OutlineAPIError: If creation fails
        """
        data: Dict[str, Any] = {
            "name": name,
            "documentId": document_id,
            "contentType": content_type,
            "size": size,
            "preset": preset,
        }
        return self._request("POST", "attachments.create", data)

    def attachments_delete(self, id: str) -> Dict:
        """
        Delete an attachment.

        Args:
            id: Attachment ID

        Returns:
            Deletion confirmation

        Raises:
            OutlineAPIError: If deletion fails
        """
        return self._request("POST", "attachments.delete", {"id": id})

    def attachments_redirect(self, id: str) -> Dict:
        """
        Get redirect URL for an attachment.

        Args:
            id: Attachment ID

        Returns:
            Dict with 'url' key containing the redirect URL

        Raises:
            OutlineAPIError: If request fails
        """
        # This endpoint returns a 302 redirect, not JSON
        # We need to capture the Location header
        data = json.dumps({"id": id}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/attachments.redirect",
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "outline-cli/0.1.0",
            },
            method="POST",
        )

        try:
            # Don't follow redirects automatically
            class NoRedirect(urllib.request.HTTPRedirectHandler):
                def redirect_request(self, req, fp, code, msg, headers, newurl):
                    return None

            opener = urllib.request.build_opener(NoRedirect)
            opener.open(req, timeout=self.timeout)
            # If we get here without redirect, something is wrong
            raise OutlineAPIError("Expected redirect but got normal response")
        except urllib.error.HTTPError as e:
            if e.code in [301, 302, 303, 307, 308]:
                # This is the expected redirect
                redirect_url = e.headers.get("Location")
                if redirect_url:
                    return {
                        "url": redirect_url,
                        "status": e.code,
                        "ok": True,
                    }
                else:
                    raise OutlineAPIError("Redirect response missing Location header")
            else:
                # This is an actual error
                try:
                    error_data = json.loads(e.read().decode("utf-8"))
                    error_message = error_data.get("message", str(e))
                except Exception:
                    error_message = str(e)
                raise OutlineAPIError(f"[HTTP {e.code}] {error_message}", status_code=e.code)

    # Share Operations

    def shares_create(self, document_id: str, published: bool = True) -> Dict:
        """
        Create a share link for a document.

        Args:
            document_id: Document ID to share
            published: Whether the share is published (default: True)

        Returns:
            Share data with URL

        Raises:
            OutlineAPIError: If creation fails
        """
        return self._request("POST", "shares.create", {"documentId": document_id, "published": published})

    def shares_list(self, document_id: Optional[str] = None, limit: int = 25, offset: int = 0) -> Dict:
        """
        List share links.

        Args:
            document_id: Optional document ID to filter by
            limit: Number of shares to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of shares

        Raises:
            OutlineAPIError: If request fails
        """
        data: Dict[str, Any] = {"limit": limit, "offset": offset}
        if document_id:
            data["documentId"] = document_id
        return self._request("POST", "shares.list", data)

    def shares_info(self, id: str) -> Dict:
        """
        Get share information.

        Args:
            id: Share ID

        Returns:
            Share data

        Raises:
            OutlineAPIError: If request fails
        """
        return self._request("POST", "shares.info", {"id": id})

    def shares_update(self, id: str, published: bool) -> Dict:
        """
        Update a share.

        Args:
            id: Share ID
            published: Whether the share is published

        Returns:
            Updated share data

        Raises:
            OutlineAPIError: If update fails
        """
        return self._request("POST", "shares.update", {"id": id, "published": published})

    def shares_revoke(self, id: str) -> Dict:
        """
        Revoke a share link.

        Args:
            id: Share ID

        Returns:
            Revocation confirmation

        Raises:
            OutlineAPIError: If revocation fails
        """
        return self._request("POST", "shares.revoke", {"id": id})

    # Star Operations

    def stars_create(self, document_id: str, index: Optional[str] = None) -> Dict:
        """
        Star (favorite) a document.

        Args:
            document_id: Document ID to star
            index: Optional index for ordering

        Returns:
            Star data

        Raises:
            OutlineAPIError: If creation fails
        """
        data: Dict[str, Any] = {"documentId": document_id}
        if index:
            data["index"] = index
        return self._request("POST", "stars.create", data)

    def stars_list(self, limit: int = 25, offset: int = 0) -> Dict:
        """
        List starred documents.

        Args:
            limit: Number of stars to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of starred documents

        Raises:
            OutlineAPIError: If request fails
        """
        return self._request("POST", "stars.list", {"limit": limit, "offset": offset})

    def stars_update(self, id: str, index: str) -> Dict:
        """
        Update a star's position/index.

        Args:
            id: Star ID
            index: New index/position for the star

        Returns:
            Updated star data

        Raises:
            OutlineAPIError: If request fails
        """
        return self._request("POST", "stars.update", {"id": id, "index": index})

    def stars_delete(self, id: str) -> Dict:
        """
        Unstar a document.

        Args:
            id: Star ID

        Returns:
            Deletion confirmation

        Raises:
            OutlineAPIError: If deletion fails
        """
        return self._request("POST", "stars.delete", {"id": id})

    # Revision Operations

    def revisions_list(self, document_id: str, limit: int = 25, offset: int = 0) -> Dict:
        """
        List document revisions.

        Args:
            document_id: Document ID
            limit: Number of revisions to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of revisions

        Raises:
            OutlineAPIError: If request fails
        """
        return self._request(
            "POST",
            "revisions.list",
            {"documentId": document_id, "limit": limit, "offset": offset},
        )

    def revisions_info(self, id: str) -> Dict:
        """
        Get revision information.

        Args:
            id: Revision ID

        Returns:
            Revision data

        Raises:
            OutlineAPIError: If request fails
        """
        return self._request("POST", "revisions.info", {"id": id})

    # Views Operations

    def views_create(self, document_id: str) -> Dict:
        """
        Create a view record for a document.

        Args:
            document_id: Document ID

        Returns:
            View data

        Raises:
            OutlineAPIError: If request fails
        """
        return self._request("POST", "views.create", {"documentId": document_id})

    def views_list(self, document_id: str, limit: int = 25, offset: int = 0) -> Dict:
        """
        List views for a document.

        Args:
            document_id: Document ID
            limit: Number of views to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of views

        Raises:
            OutlineAPIError: If request fails
        """
        return self._request(
            "POST",
            "views.list",
            {"documentId": document_id, "limit": limit, "offset": offset},
        )

    # Event Operations

    def events_list(
        self,
        name: Optional[str] = None,
        actor_id: Optional[str] = None,
        document_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> Dict:
        """
        List events (audit log).

        Args:
            name: Optional event name filter
            actor_id: Optional actor (user) ID filter
            document_id: Optional document ID filter
            collection_id: Optional collection ID filter
            limit: Number of events to return (default: 25)
            offset: Pagination offset (default: 0)

        Returns:
            List of events

        Raises:
            OutlineAPIError: If request fails
        """
        data: Dict[str, Any] = {"limit": limit, "offset": offset}
        if name:
            data["name"] = name
        if actor_id:
            data["actorId"] = actor_id
        if document_id:
            data["documentId"] = document_id
        if collection_id:
            data["collectionId"] = collection_id
        return self._request("POST", "events.list", data)
