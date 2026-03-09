#!/usr/bin/env python3
"""
Main CLI entry point for Outline CLI.

This module provides the main command-line interface for the outline-cli package.
"""

import argparse
import json
import sys
from typing import Callable

from outline_cli import OutlineAPIError, OutlineClient, OutlineValidationError
from outline_cli.comment_utils import build_comment_data

CommandHandler = Callable[[OutlineClient, argparse.Namespace], int]


def create_document(client: OutlineClient, args):
    """Create a new document."""
    try:
        result = client.documents_create(
            title=args.title,
            text=args.text,
            collection_id=args.collection_id,
            parent_document_id=args.parent_id,
            publish=not args.draft,
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def get_document(client: OutlineClient, args):
    """Get document information."""
    try:
        result = client.documents_info(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_documents(client: OutlineClient, args):
    """List documents."""
    try:
        result = client.documents_list(
            collection_id=args.collection_id,
            limit=args.limit,
            offset=args.offset,
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def update_document(client: OutlineClient, args):
    """Update a document."""
    try:
        result = client.documents_update(
            id=args.id,
            title=args.title,
            text=args.text,
            publish=args.publish if args.publish is not None else None,
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def delete_document(client: OutlineClient, args):
    """Delete a document."""
    try:
        result = client.documents_delete(id=args.id, permanent=args.permanent)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def archive_document(client: OutlineClient, args):
    """Archive a document."""
    try:
        result = client.documents_archive(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def restore_document(client: OutlineClient, args):
    """Restore an archived document."""
    try:
        result = client.documents_restore(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def move_document(client: OutlineClient, args):
    """Move a document."""
    try:
        result = client.documents_move(
            id=args.id,
            collection_id=args.collection_id if hasattr(args, "collection_id") and args.collection_id else None,
            parent_document_id=args.parent_id if hasattr(args, "parent_id") and args.parent_id else None,
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def duplicate_document(client: OutlineClient, args):
    """Duplicate a document."""
    try:
        result = client.documents_duplicate(
            id=args.id,
            title=args.title if hasattr(args, "title") and args.title else None,
            collection_id=args.collection_id if hasattr(args, "collection_id") and args.collection_id else None,
            parent_document_id=args.parent_id if hasattr(args, "parent_id") and args.parent_id else None,
            publish=not args.draft if hasattr(args, "draft") else False,
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def templatize_document(client: OutlineClient, args):
    """Convert a document to a template."""
    try:
        result = client.documents_templatize(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def export_document(client: OutlineClient, args):
    """Export a document."""
    try:
        result = client.documents_export(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def import_document(client: OutlineClient, args):
    """Import a document."""
    try:
        result = client.documents_import(
            file=args.file,
            collection_id=args.collection_id,
            parent_document_id=args.parent_id if hasattr(args, "parent_id") and args.parent_id else None,
            publish=not args.draft if hasattr(args, "draft") else True,
        )
        print(json.dumps(result, indent=2))
        return 0
    except (OutlineAPIError, OutlineValidationError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_drafts(client: OutlineClient, args):
    """List draft documents."""
    try:
        result = client.documents_drafts(
            collection_id=args.collection_id if hasattr(args, "collection_id") and args.collection_id else None,
            limit=args.limit,
            offset=args.offset,
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_archived_documents(client: OutlineClient, args):
    """List archived documents."""
    try:
        result = client.documents_archived(limit=args.limit, offset=args.offset)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_deleted_documents(client: OutlineClient, args):
    """List deleted documents."""
    try:
        result = client.documents_deleted(limit=args.limit, offset=args.offset)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_viewed_documents(client: OutlineClient, args):
    """List recently viewed documents."""
    try:
        result = client.documents_viewed(limit=args.limit, offset=args.offset)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def empty_trash(client: OutlineClient, args):
    """Empty the trash."""
    try:
        result = client.documents_empty_trash()
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def unpublish_document(client: OutlineClient, args):
    """Unpublish a document."""
    try:
        result = client.documents_unpublish(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def add_user_to_document(client: OutlineClient, args):
    """Add a user to a document."""
    try:
        result = client.documents_add_user(
            id=args.id,
            user_id=args.user_id,
            permission=args.permission if hasattr(args, "permission") and args.permission else "read",
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def remove_user_from_document(client: OutlineClient, args):
    """Remove a user from a document."""
    try:
        result = client.documents_remove_user(id=args.id, user_id=args.user_id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_document_memberships(client: OutlineClient, args):
    """List document user memberships."""
    try:
        result = client.documents_memberships(
            id=args.id,
            query=args.query if hasattr(args, "query") and args.query else None,
            limit=args.limit,
            offset=args.offset,
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_document_users(client: OutlineClient, args):
    """List users with access to a document."""
    try:
        result = client.documents_users(
            id=args.id,
            query=args.query if hasattr(args, "query") and args.query else None,
            limit=args.limit,
            offset=args.offset,
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def add_group_to_document(client: OutlineClient, args):
    """Add a group to a document."""
    try:
        result = client.documents_add_group(
            id=args.id,
            group_id=args.group_id,
            permission=args.permission if hasattr(args, "permission") and args.permission else "read",
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def remove_group_from_document(client: OutlineClient, args):
    """Remove a group from a document."""
    try:
        result = client.documents_remove_group(id=args.id, group_id=args.group_id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_document_group_memberships(client: OutlineClient, args):
    """List document group memberships."""
    try:
        result = client.documents_group_memberships(
            id=args.id,
            query=args.query if hasattr(args, "query") and args.query else None,
            limit=args.limit,
            offset=args.offset,
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_collections(client: OutlineClient, args):
    """List all collections."""
    try:
        result = client.collections_list(limit=args.limit, offset=args.offset)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def get_collection(client: OutlineClient, args):
    """Get collection information."""
    try:
        result = client.collections_info(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def create_collection(client: OutlineClient, args):
    """Create a new collection."""
    try:
        result = client.collections_create(
            name=args.name,
            description=args.description,
            color=args.color,
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def update_collection(client: OutlineClient, args):
    """Update a collection."""
    try:
        result = client.collections_update(
            id=args.id,
            name=args.name,
            description=args.description,
            color=args.color,
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def delete_collection(client: OutlineClient, args):
    """Delete a collection."""
    try:
        result = client.collections_delete(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_collection_documents(client: OutlineClient, args):
    """List documents in a collection."""
    try:
        result = client.collections_documents(id=args.id, limit=args.limit, offset=args.offset)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def add_user_to_collection(client: OutlineClient, args):
    """Add a user to a collection."""
    try:
        result = client.collections_add_user(
            id=args.id,
            user_id=args.user_id,
            permission=args.permission if hasattr(args, "permission") and args.permission else "read",
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def remove_user_from_collection(client: OutlineClient, args):
    """Remove a user from a collection."""
    try:
        result = client.collections_remove_user(id=args.id, user_id=args.user_id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_collection_memberships(client: OutlineClient, args):
    """List collection user memberships."""
    try:
        result = client.collections_memberships(
            id=args.id,
            query=args.query if hasattr(args, "query") and args.query else None,
            limit=args.limit,
            offset=args.offset,
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def add_group_to_collection(client: OutlineClient, args):
    """Add a group to a collection."""
    try:
        result = client.collections_add_group(
            id=args.id,
            group_id=args.group_id,
            permission=args.permission if hasattr(args, "permission") and args.permission else "read",
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def remove_group_from_collection(client: OutlineClient, args):
    """Remove a group from a collection."""
    try:
        result = client.collections_remove_group(id=args.id, group_id=args.group_id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_collection_group_memberships(client: OutlineClient, args):
    """List collection group memberships."""
    try:
        result = client.collections_group_memberships(
            id=args.id,
            query=args.query if hasattr(args, "query") and args.query else None,
            limit=args.limit,
            offset=args.offset,
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def export_collection(client: OutlineClient, args):
    """Export a collection."""
    try:
        result = client.collections_export(
            id=args.id, format=args.format if hasattr(args, "format") and args.format else "outline-markdown"
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def export_all_collections(client: OutlineClient, args):
    """Export all collections."""
    try:
        result = client.collections_export_all(
            format=args.format if hasattr(args, "format") and args.format else "outline-markdown"
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def search_documents(client: OutlineClient, args: argparse.Namespace) -> int:
    """Search documents."""
    try:
        if args.titles_only:
            result = client.documents_search_titles(
                query=args.query,
                collection_id=args.collection_id,
                limit=args.limit,
            )
        else:
            result = client.documents_search(
                query=args.query,
                collection_id=args.collection_id,
                limit=args.limit,
            )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def get_auth_info(client: OutlineClient, args) -> int:
    """Get current authentication and user information."""
    try:
        result = client.auth_info()
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_users(client: OutlineClient, args):
    """List all users."""
    try:
        result = client.users_list(
            limit=args.limit, offset=args.offset, query=args.query if hasattr(args, "query") else None
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def get_user(client: OutlineClient, args):
    """Get user information."""
    try:
        result = client.users_info(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def invite_user(client: OutlineClient, args):
    """Invite a new user."""
    try:
        result = client.users_invite(
            email=args.email,
            name=args.name if hasattr(args, "name") and args.name else None,
            role=args.role if hasattr(args, "role") and args.role else "member",
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def update_user(client: OutlineClient, args):
    """Update user information."""
    try:
        result = client.users_update(
            id=args.id,
            name=args.name if hasattr(args, "name") and args.name else None,
            avatar_url=args.avatar_url if hasattr(args, "avatar_url") and args.avatar_url else None,
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def update_user_role(client: OutlineClient, args):
    """Update user role."""
    try:
        result = client.users_update_role(id=args.id, role=args.role)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def suspend_user(client: OutlineClient, args):
    """Suspend a user."""
    try:
        result = client.users_suspend(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def activate_user(client: OutlineClient, args):
    """Activate a suspended user."""
    try:
        result = client.users_activate(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def delete_user(client: OutlineClient, args):
    """Delete a user."""
    try:
        result = client.users_delete(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_groups(client: OutlineClient, args):
    """List all groups."""
    try:
        result = client.groups_list(limit=args.limit, offset=args.offset)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def get_group(client: OutlineClient, args):
    """Get group information."""
    try:
        result = client.groups_info(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def create_group(client: OutlineClient, args):
    """Create a new group."""
    try:
        result = client.groups_create(name=args.name)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def update_group(client: OutlineClient, args):
    """Update a group."""
    try:
        result = client.groups_update(id=args.id, name=args.name)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def delete_group(client: OutlineClient, args):
    """Delete a group."""
    try:
        result = client.groups_delete(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def add_user_to_group(client: OutlineClient, args):
    """Add a user to a group."""
    try:
        result = client.groups_add_user(id=args.id, user_id=args.user_id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def remove_user_from_group(client: OutlineClient, args):
    """Remove a user from a group."""
    try:
        result = client.groups_remove_user(id=args.id, user_id=args.user_id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_group_memberships(client: OutlineClient, args):
    """List group user memberships."""
    try:
        result = client.groups_memberships(
            id=args.id,
            query=args.query if hasattr(args, "query") and args.query else None,
            limit=args.limit,
            offset=args.offset,
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_file_operations(client: OutlineClient, args):
    """List file operations."""
    try:
        result = client.file_operations_list(
            type=args.type if hasattr(args, "type") and args.type else "export", limit=args.limit, offset=args.offset
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def get_file_operation(client: OutlineClient, args):
    """Get file operation information."""
    try:
        result = client.file_operations_info(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def redirect_file_operation(client: OutlineClient, args):
    """Get file operation redirect URL."""
    try:
        result = client.file_operations_redirect(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def delete_file_operation(client: OutlineClient, args):
    """Delete a file operation."""
    try:
        result = client.file_operations_delete(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_comments(client: OutlineClient, args):
    """List comments on a document."""
    try:
        result = client.comments_list(document_id=args.document_id, limit=args.limit, offset=args.offset)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def get_comment(client: OutlineClient, args):
    """Get comment information."""
    try:
        result = client.comments_info(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def create_comment(client: OutlineClient, args):
    """Create a new comment."""
    try:
        results = client.comments_create_markdown(
            document_id=args.document_id,
            text=args.data,
            parent_comment_id=args.parent_id if hasattr(args, "parent_id") else None,
        )
        if len(results) == 1:
            print(json.dumps(results[0], indent=2))
        else:
            print(json.dumps({"split": True, "chunkCount": len(results), "results": results}, indent=2))
        return 0
    except (OutlineAPIError, OutlineValidationError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def update_comment(client: OutlineClient, args):
    """Update a comment."""
    try:
        comment_data = build_comment_data(args.data)
        result = client.comments_update(id=args.id, data=comment_data)
        print(json.dumps(result, indent=2))
        return 0
    except (OutlineAPIError, OutlineValidationError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def delete_comment(client: OutlineClient, args):
    """Delete a comment."""
    try:
        result = client.comments_delete(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def resolve_comment(client: OutlineClient, args):
    """Mark a comment as resolved."""
    try:
        result = client.comments_resolve(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def unresolve_comment(client: OutlineClient, args):
    """Mark a comment as unresolved."""
    try:
        result = client.comments_unresolve(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def add_comment_reaction(client: OutlineClient, args):
    """Add an emoji reaction to a comment."""
    try:
        result = client.comments_add_reaction(id=args.id, emoji=args.emoji)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def remove_comment_reaction(client: OutlineClient, args):
    """Remove an emoji reaction from a comment."""
    try:
        result = client.comments_remove_reaction(id=args.id, emoji=args.emoji)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def create_attachment(client: OutlineClient, args):
    """Create an attachment."""
    try:
        result = client.attachments_create(
            name=args.name,
            document_id=args.document_id,
            content_type=args.content_type,
            size=args.size,
            preset=args.preset,
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def delete_attachment(client: OutlineClient, args):
    """Delete an attachment."""
    try:
        result = client.attachments_delete(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def redirect_attachment(client: OutlineClient, args):
    """Get redirect URL for an attachment."""
    try:
        result = client.attachments_redirect(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def create_share(client: OutlineClient, args):
    """Create a share link."""
    try:
        result = client.shares_create(
            document_id=args.document_id, published=not args.unpublished if hasattr(args, "unpublished") else True
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_shares(client: OutlineClient, args):
    """List share links."""
    try:
        result = client.shares_list(
            document_id=args.document_id if hasattr(args, "document_id") and args.document_id else None,
            limit=args.limit,
            offset=args.offset,
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def get_share(client: OutlineClient, args):
    """Get share information."""
    try:
        result = client.shares_info(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def revoke_share(client: OutlineClient, args):
    """Revoke a share link."""
    try:
        result = client.shares_revoke(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def update_share(client: OutlineClient, args):
    """Update a share link."""
    try:
        result = client.shares_update(id=args.id, published=args.published)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def create_star(client: OutlineClient, args):
    """Star a document."""
    try:
        result = client.stars_create(document_id=args.document_id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_stars(client: OutlineClient, args):
    """List starred documents."""
    try:
        result = client.stars_list(limit=args.limit, offset=args.offset)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def delete_star(client: OutlineClient, args):
    """Unstar a document."""
    try:
        result = client.stars_delete(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def update_star(client: OutlineClient, args):
    """Update a star's position."""
    try:
        result = client.stars_update(id=args.id, index=args.index)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def create_view(client: OutlineClient, args):
    """Create a view record for a document."""
    try:
        result = client.views_create(document_id=args.document_id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_views(client: OutlineClient, args):
    """List views for a document."""
    try:
        result = client.views_list(
            document_id=args.document_id,
            limit=args.limit,
            offset=args.offset,
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_revisions(client: OutlineClient, args):
    """List document revisions."""
    try:
        result = client.revisions_list(document_id=args.document_id, limit=args.limit, offset=args.offset)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def get_revision(client: OutlineClient, args):
    """Get revision information."""
    try:
        result = client.revisions_info(id=args.id)
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_events(client: OutlineClient, args):
    """List events."""
    try:
        result = client.events_list(
            name=args.name if hasattr(args, "name") and args.name else None,
            actor_id=args.actor_id if hasattr(args, "actor_id") and args.actor_id else None,
            document_id=args.document_id if hasattr(args, "document_id") and args.document_id else None,
            collection_id=args.collection_id if hasattr(args, "collection_id") and args.collection_id else None,
            limit=args.limit,
            offset=args.offset,
        )
        print(json.dumps(result, indent=2))
        return 0
    except OutlineAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="outline-cli",
        description="Outline CLI - Interact with Outline knowledge bases",
        epilog="For more information, see: https://github.com/visualdust/outline-skills",
    )
    parser.add_argument("--version", action="version", version="outline-cli 0.1.3")
    parser.add_argument("--api-key", help="Outline API key")
    parser.add_argument("--base-url", help="Outline API base URL")
    parser.add_argument("--timeout", type=int, help="Request timeout in seconds")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Documents subcommand
    docs_parser = subparsers.add_parser("documents", aliases=["docs", "doc"], help="Document operations")
    docs_subparsers = docs_parser.add_subparsers(dest="subcommand", help="Document commands")

    # Documents: create
    docs_create = docs_subparsers.add_parser("create", help="Create a new document")
    docs_create.add_argument("--title", required=True, help="Document title")
    docs_create.add_argument("--text", required=True, help="Document content (Markdown)")
    docs_create.add_argument("--collection-id", required=True, help="Collection ID")
    docs_create.add_argument("--parent-id", help="Parent document ID (for nested documents)")
    docs_create.add_argument("--draft", action="store_true", help="Create as draft (unpublished)")

    # Documents: info
    docs_info = docs_subparsers.add_parser("info", help="Get document information")
    docs_info.add_argument("--id", required=True, help="Document ID")

    # Documents: list
    docs_list = docs_subparsers.add_parser("list", help="List documents")
    docs_list.add_argument("--collection-id", help="Filter by collection ID")
    docs_list.add_argument("--limit", type=int, default=25, help="Number of documents to return")
    docs_list.add_argument("--offset", type=int, default=0, help="Pagination offset")

    # Documents: update
    docs_update = docs_subparsers.add_parser("update", help="Update a document")
    docs_update.add_argument("--id", required=True, help="Document ID")
    docs_update.add_argument("--title", help="New title")
    docs_update.add_argument("--text", help="New content")
    publish_group = docs_update.add_mutually_exclusive_group()
    publish_group.add_argument("--publish", dest="publish", action="store_true", help="Publish the document")
    publish_group.add_argument("--unpublish", dest="publish", action="store_false", help="Unpublish the document")
    docs_update.set_defaults(publish=None)

    # Documents: delete
    docs_delete = docs_subparsers.add_parser("delete", help="Delete a document")
    docs_delete.add_argument("--id", required=True, help="Document ID")
    docs_delete.add_argument("--permanent", action="store_true", help="Permanently delete (cannot be restored)")

    # Documents: archive
    docs_archive = docs_subparsers.add_parser("archive", help="Archive a document")
    docs_archive.add_argument("--id", required=True, help="Document ID")

    # Documents: restore
    docs_restore = docs_subparsers.add_parser("restore", help="Restore an archived document")
    docs_restore.add_argument("--id", required=True, help="Document ID")

    # Documents: move
    docs_move = docs_subparsers.add_parser("move", help="Move a document")
    docs_move.add_argument("--id", required=True, help="Document ID")
    docs_move.add_argument("--collection-id", help="New collection ID")
    docs_move.add_argument("--parent-id", help="New parent document ID")

    # Documents: duplicate
    docs_duplicate = docs_subparsers.add_parser("duplicate", help="Duplicate a document")
    docs_duplicate.add_argument("--id", required=True, help="Document ID")
    docs_duplicate.add_argument("--title", help="Title for the duplicate")
    docs_duplicate.add_argument("--collection-id", help="Collection ID for the duplicate")
    docs_duplicate.add_argument("--parent-id", help="Parent document ID")
    docs_duplicate.add_argument("--draft", action="store_true", help="Create as draft")

    # Documents: templatize
    docs_templatize = docs_subparsers.add_parser("templatize", help="Convert document to template")
    docs_templatize.add_argument("--id", required=True, help="Document ID")

    # Documents: export
    docs_export = docs_subparsers.add_parser("export", help="Export document as Markdown")
    docs_export.add_argument("--id", required=True, help="Document ID")

    # Documents: import
    docs_import = docs_subparsers.add_parser("import", help="Import a local file")
    docs_import.add_argument("--file", required=True, help="Path to a local file")
    docs_import.add_argument("--collection-id", required=True, help="Collection ID")
    docs_import.add_argument("--parent-id", help="Parent document ID")
    docs_import.add_argument("--draft", action="store_true", help="Create as draft")

    # Documents: drafts
    docs_drafts = docs_subparsers.add_parser("drafts", help="List draft documents")
    docs_drafts.add_argument("--collection-id", help="Filter by collection ID")
    docs_drafts.add_argument("--limit", type=int, default=25, help="Number of documents to return")
    docs_drafts.add_argument("--offset", type=int, default=0, help="Pagination offset")

    # Documents: archived
    docs_archived = docs_subparsers.add_parser("archived", help="List archived documents")
    docs_archived.add_argument("--limit", type=int, default=25, help="Number of documents to return")
    docs_archived.add_argument("--offset", type=int, default=0, help="Pagination offset")

    # Documents: deleted
    docs_deleted = docs_subparsers.add_parser("deleted", help="List deleted documents")
    docs_deleted.add_argument("--limit", type=int, default=25, help="Number of documents to return")
    docs_deleted.add_argument("--offset", type=int, default=0, help="Pagination offset")

    # Documents: viewed
    docs_viewed = docs_subparsers.add_parser("viewed", help="List recently viewed documents")
    docs_viewed.add_argument("--limit", type=int, default=25, help="Number of documents to return")
    docs_viewed.add_argument("--offset", type=int, default=0, help="Pagination offset")

    # Documents: empty-trash
    docs_subparsers.add_parser("empty-trash", help="Empty the trash")

    # Documents: unpublish
    docs_unpublish = docs_subparsers.add_parser("unpublish", help="Unpublish a document")
    docs_unpublish.add_argument("--id", required=True, help="Document ID")

    # Documents: add-user
    docs_add_user = docs_subparsers.add_parser("add-user", help="Add a user to a document")
    docs_add_user.add_argument("--id", required=True, help="Document ID")
    docs_add_user.add_argument("--user-id", required=True, help="User ID")
    docs_add_user.add_argument("--permission", choices=["read", "read_write"], default="read", help="Permission level")

    # Documents: remove-user
    docs_remove_user = docs_subparsers.add_parser("remove-user", help="Remove a user from a document")
    docs_remove_user.add_argument("--id", required=True, help="Document ID")
    docs_remove_user.add_argument("--user-id", required=True, help="User ID")

    # Documents: memberships
    docs_memberships = docs_subparsers.add_parser("memberships", help="List document user memberships")
    docs_memberships.add_argument("--id", required=True, help="Document ID")
    docs_memberships.add_argument("--query", help="Search query to filter users")
    docs_memberships.add_argument("--limit", type=int, default=25, help="Number of memberships to return")
    docs_memberships.add_argument("--offset", type=int, default=0, help="Pagination offset")

    # Documents: users
    docs_users = docs_subparsers.add_parser("users", help="List users with access to a document")
    docs_users.add_argument("--id", required=True, help="Document ID")
    docs_users.add_argument("--query", help="Search query to filter users")
    docs_users.add_argument("--limit", type=int, default=25, help="Number of users to return")
    docs_users.add_argument("--offset", type=int, default=0, help="Pagination offset")

    # Documents: add-group
    docs_add_group = docs_subparsers.add_parser("add-group", help="Add a group to a document")
    docs_add_group.add_argument("--id", required=True, help="Document ID")
    docs_add_group.add_argument("--group-id", required=True, help="Group ID")
    docs_add_group.add_argument("--permission", choices=["read", "read_write"], default="read", help="Permission level")

    # Documents: remove-group
    docs_remove_group = docs_subparsers.add_parser("remove-group", help="Remove a group from a document")
    docs_remove_group.add_argument("--id", required=True, help="Document ID")
    docs_remove_group.add_argument("--group-id", required=True, help="Group ID")

    # Documents: group-memberships
    docs_group_memberships = docs_subparsers.add_parser("group-memberships", help="List document group memberships")
    docs_group_memberships.add_argument("--id", required=True, help="Document ID")
    docs_group_memberships.add_argument("--query", help="Search query to filter groups")
    docs_group_memberships.add_argument("--limit", type=int, default=25, help="Number of memberships to return")
    docs_group_memberships.add_argument("--offset", type=int, default=0, help="Pagination offset")

    # Collections subcommand
    colls_parser = subparsers.add_parser("collections", aliases=["colls", "coll"], help="Collection operations")
    colls_subparsers = colls_parser.add_subparsers(dest="subcommand", help="Collection commands")

    # Collections: list
    colls_list = colls_subparsers.add_parser("list", help="List all collections")
    colls_list.add_argument("--limit", type=int, default=25, help="Number of collections to return")
    colls_list.add_argument("--offset", type=int, default=0, help="Pagination offset")

    # Collections: info
    colls_info = colls_subparsers.add_parser("info", help="Get collection information")
    colls_info.add_argument("--id", required=True, help="Collection ID")

    # Collections: create
    colls_create = colls_subparsers.add_parser("create", help="Create a new collection")
    colls_create.add_argument("--name", required=True, help="Collection name")
    colls_create.add_argument("--description", help="Collection description")
    colls_create.add_argument("--color", help="Collection color (hex format)")

    # Collections: update
    colls_update = colls_subparsers.add_parser("update", help="Update a collection")
    colls_update.add_argument("--id", required=True, help="Collection ID")
    colls_update.add_argument("--name", help="New name")
    colls_update.add_argument("--description", help="New description")
    colls_update.add_argument("--color", help="New color (hex format)")

    # Collections: delete
    colls_delete = colls_subparsers.add_parser("delete", help="Delete a collection")
    colls_delete.add_argument("--id", required=True, help="Collection ID")

    # Collections: documents
    colls_documents = colls_subparsers.add_parser("documents", help="List documents in a collection")
    colls_documents.add_argument("--id", required=True, help="Collection ID")
    colls_documents.add_argument("--limit", type=int, default=25, help="Number of documents to return")
    colls_documents.add_argument("--offset", type=int, default=0, help="Pagination offset")

    # Collections: add-user
    colls_add_user = colls_subparsers.add_parser("add-user", help="Add a user to a collection")
    colls_add_user.add_argument("--id", required=True, help="Collection ID")
    colls_add_user.add_argument("--user-id", required=True, help="User ID")
    colls_add_user.add_argument(
        "--permission", choices=["read", "read_write", "admin"], default="read", help="Permission level"
    )

    # Collections: remove-user
    colls_remove_user = colls_subparsers.add_parser("remove-user", help="Remove a user from a collection")
    colls_remove_user.add_argument("--id", required=True, help="Collection ID")
    colls_remove_user.add_argument("--user-id", required=True, help="User ID")

    # Collections: memberships
    colls_memberships = colls_subparsers.add_parser("memberships", help="List collection user memberships")
    colls_memberships.add_argument("--id", required=True, help="Collection ID")
    colls_memberships.add_argument("--query", help="Search query to filter users")
    colls_memberships.add_argument("--limit", type=int, default=25, help="Number of memberships to return")
    colls_memberships.add_argument("--offset", type=int, default=0, help="Pagination offset")

    # Collections: add-group
    colls_add_group = colls_subparsers.add_parser("add-group", help="Add a group to a collection")
    colls_add_group.add_argument("--id", required=True, help="Collection ID")
    colls_add_group.add_argument("--group-id", required=True, help="Group ID")
    colls_add_group.add_argument(
        "--permission", choices=["read", "read_write", "admin"], default="read", help="Permission level"
    )

    # Collections: remove-group
    colls_remove_group = colls_subparsers.add_parser("remove-group", help="Remove a group from a collection")
    colls_remove_group.add_argument("--id", required=True, help="Collection ID")
    colls_remove_group.add_argument("--group-id", required=True, help="Group ID")

    # Collections: group-memberships
    colls_group_memberships = colls_subparsers.add_parser("group-memberships", help="List collection group memberships")
    colls_group_memberships.add_argument("--id", required=True, help="Collection ID")
    colls_group_memberships.add_argument("--query", help="Search query to filter groups")
    colls_group_memberships.add_argument("--limit", type=int, default=25, help="Number of memberships to return")
    colls_group_memberships.add_argument("--offset", type=int, default=0, help="Pagination offset")

    # Collections: export
    colls_export = colls_subparsers.add_parser("export", help="Export a collection")
    colls_export.add_argument("--id", required=True, help="Collection ID")
    colls_export.add_argument("--format", default="outline-markdown", help="Export format")

    # Collections: export-all
    colls_export_all = colls_subparsers.add_parser("export-all", help="Export all collections")
    colls_export_all.add_argument("--format", default="outline-markdown", help="Export format")

    # Search subcommand
    search_parser = subparsers.add_parser("search", help="Search documents")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--collection-id", help="Limit search to specific collection")
    search_parser.add_argument("--limit", type=int, default=25, help="Maximum number of results")
    search_parser.add_argument("--titles-only", action="store_true", help="Search titles only (faster)")

    # Auth subcommand
    auth_parser = subparsers.add_parser("auth", help="Authentication operations")
    auth_subparsers = auth_parser.add_subparsers(dest="subcommand", help="Auth commands")

    # Auth: info
    auth_subparsers.add_parser("info", help="Get current user and authentication information")

    # Users subcommand
    users_parser = subparsers.add_parser("users", help="User operations")
    users_subparsers = users_parser.add_subparsers(dest="subcommand", help="User commands")

    # Users: list
    users_list = users_subparsers.add_parser("list", help="List all users")
    users_list.add_argument("--limit", type=int, default=25, help="Number of users to return")
    users_list.add_argument("--offset", type=int, default=0, help="Pagination offset")
    users_list.add_argument("--query", help="Search query to filter users")

    # Users: info
    users_info = users_subparsers.add_parser("info", help="Get user information")
    users_info.add_argument("--id", required=True, help="User ID")

    # Users: invite
    users_invite = users_subparsers.add_parser("invite", help="Invite a new user")
    users_invite.add_argument("--email", required=True, help="User email address")
    users_invite.add_argument("--name", help="User name")
    users_invite.add_argument("--role", choices=["member", "viewer", "admin"], default="member", help="User role")

    # Users: update
    users_update = users_subparsers.add_parser("update", help="Update user information")
    users_update.add_argument("--id", required=True, help="User ID")
    users_update.add_argument("--name", help="New name")
    users_update.add_argument("--avatar-url", help="New avatar URL")

    # Users: update-role
    users_update_role = users_subparsers.add_parser("update-role", help="Update user role")
    users_update_role.add_argument("--id", required=True, help="User ID")
    users_update_role.add_argument("--role", required=True, choices=["member", "viewer", "admin"], help="New role")

    # Users: suspend
    users_suspend = users_subparsers.add_parser("suspend", help="Suspend a user")
    users_suspend.add_argument("--id", required=True, help="User ID")

    # Users: activate
    users_activate = users_subparsers.add_parser("activate", help="Activate a suspended user")
    users_activate.add_argument("--id", required=True, help="User ID")

    # Users: delete
    users_delete = users_subparsers.add_parser("delete", help="Delete a user")
    users_delete.add_argument("--id", required=True, help="User ID")

    # Groups subcommand
    groups_parser = subparsers.add_parser("groups", help="Group operations")
    groups_subparsers = groups_parser.add_subparsers(dest="subcommand", help="Group commands")

    # Groups: list
    groups_list = groups_subparsers.add_parser("list", help="List all groups")
    groups_list.add_argument("--limit", type=int, default=25, help="Number of groups to return")
    groups_list.add_argument("--offset", type=int, default=0, help="Pagination offset")

    # Groups: info
    groups_info = groups_subparsers.add_parser("info", help="Get group information")
    groups_info.add_argument("--id", required=True, help="Group ID")

    # Groups: create
    groups_create = groups_subparsers.add_parser("create", help="Create a new group")
    groups_create.add_argument("--name", required=True, help="Group name")

    # Groups: update
    groups_update = groups_subparsers.add_parser("update", help="Update a group")
    groups_update.add_argument("--id", required=True, help="Group ID")
    groups_update.add_argument("--name", required=True, help="New group name")

    # Groups: delete
    groups_delete = groups_subparsers.add_parser("delete", help="Delete a group")
    groups_delete.add_argument("--id", required=True, help="Group ID")

    # Groups: add-user
    groups_add_user = groups_subparsers.add_parser("add-user", help="Add a user to a group")
    groups_add_user.add_argument("--id", required=True, help="Group ID")
    groups_add_user.add_argument("--user-id", required=True, help="User ID")

    # Groups: remove-user
    groups_remove_user = groups_subparsers.add_parser("remove-user", help="Remove a user from a group")
    groups_remove_user.add_argument("--id", required=True, help="Group ID")
    groups_remove_user.add_argument("--user-id", required=True, help="User ID")

    # Groups: memberships
    groups_memberships = groups_subparsers.add_parser("memberships", help="List group user memberships")
    groups_memberships.add_argument("--id", required=True, help="Group ID")
    groups_memberships.add_argument("--query", help="Search query to filter users")
    groups_memberships.add_argument("--limit", type=int, default=25, help="Number of memberships to return")
    groups_memberships.add_argument("--offset", type=int, default=0, help="Pagination offset")

    # File Operations subcommand
    file_ops_parser = subparsers.add_parser("file-operations", aliases=["fileops"], help="File operation operations")
    file_ops_subparsers = file_ops_parser.add_subparsers(dest="subcommand", help="File operation commands")

    # File Operations: list
    file_ops_list = file_ops_subparsers.add_parser("list", help="List file operations")
    file_ops_list.add_argument(
        "--type", choices=["import", "export"], default="export", help="Filter by operation type"
    )
    file_ops_list.add_argument("--limit", type=int, default=25, help="Number of operations to return")
    file_ops_list.add_argument("--offset", type=int, default=0, help="Pagination offset")

    # File Operations: info
    file_ops_info = file_ops_subparsers.add_parser("info", help="Get file operation information")
    file_ops_info.add_argument("--id", required=True, help="File operation ID")

    # File Operations: redirect
    file_ops_redirect = file_ops_subparsers.add_parser("redirect", help="Get file operation download URL")
    file_ops_redirect.add_argument("--id", required=True, help="File operation ID")

    # File Operations: delete
    file_ops_delete = file_ops_subparsers.add_parser("delete", help="Delete a file operation")
    file_ops_delete.add_argument("--id", required=True, help="File operation ID")

    # Comments subcommand
    comments_parser = subparsers.add_parser("comments", help="Comment operations")
    comments_subparsers = comments_parser.add_subparsers(dest="subcommand", help="Comment commands")

    # Comments: list
    comments_list = comments_subparsers.add_parser("list", help="List comments on a document")
    comments_list.add_argument("--document-id", required=True, help="Document ID")
    comments_list.add_argument("--limit", type=int, default=25, help="Number of comments to return")
    comments_list.add_argument("--offset", type=int, default=0, help="Pagination offset")

    # Comments: info
    comments_info = comments_subparsers.add_parser("info", help="Get comment information")
    comments_info.add_argument("--id", required=True, help="Comment ID")

    # Comments: create
    comments_create = comments_subparsers.add_parser("create", help="Create a new comment")
    comments_create.add_argument("--document-id", required=True, help="Document ID")
    comments_create.add_argument(
        "--data",
        required=True,
        help="Comment Markdown text. Long content is auto-split into numbered replies.",
    )
    comments_create.add_argument("--parent-id", help="Parent comment ID for replies")

    # Comments: update
    comments_update = comments_subparsers.add_parser("update", help="Update a comment")
    comments_update.add_argument("--id", required=True, help="Comment ID")
    comments_update.add_argument("--data", required=True, help="New comment text")

    # Comments: delete
    comments_delete = comments_subparsers.add_parser("delete", help="Delete a comment")
    comments_delete.add_argument("--id", required=True, help="Comment ID")

    # Comments: resolve
    comments_resolve = comments_subparsers.add_parser("resolve", help="Mark comment as resolved")
    comments_resolve.add_argument("--id", required=True, help="Comment ID")

    # Comments: unresolve
    comments_unresolve = comments_subparsers.add_parser("unresolve", help="Mark comment as unresolved")
    comments_unresolve.add_argument("--id", required=True, help="Comment ID")

    # Comments: add-reaction
    comments_add_reaction = comments_subparsers.add_parser("add-reaction", help="Add emoji reaction to comment")
    comments_add_reaction.add_argument("--id", required=True, help="Comment ID")
    comments_add_reaction.add_argument("--emoji", required=True, help="Emoji character (e.g., 👍, ❤️, 😊)")

    # Comments: remove-reaction
    comments_remove_reaction = comments_subparsers.add_parser(
        "remove-reaction", help="Remove emoji reaction from comment"
    )
    comments_remove_reaction.add_argument("--id", required=True, help="Comment ID")
    comments_remove_reaction.add_argument("--emoji", required=True, help="Emoji character to remove")

    # Attachments subcommand
    attachments_parser = subparsers.add_parser("attachments", help="Attachment operations")
    attachments_subparsers = attachments_parser.add_subparsers(dest="subcommand", help="Attachment commands")

    # Attachments: create
    attachments_create = attachments_subparsers.add_parser("create", help="Create an attachment")
    attachments_create.add_argument("--name", required=True, help="Attachment filename")
    attachments_create.add_argument("--document-id", required=True, help="Document ID")
    attachments_create.add_argument("--content-type", required=True, help="MIME type (e.g., image/png)")
    attachments_create.add_argument("--size", type=int, required=True, help="File size in bytes")
    attachments_create.add_argument("--preset", default="documentAttachment", help="Upload preset")

    # Attachments: delete
    attachments_delete = attachments_subparsers.add_parser("delete", help="Delete an attachment")
    attachments_delete.add_argument("--id", required=True, help="Attachment ID")

    # Attachments: redirect
    attachments_redirect = attachments_subparsers.add_parser("redirect", help="Get attachment redirect URL")
    attachments_redirect.add_argument("--id", required=True, help="Attachment ID")

    # Shares subcommand
    shares_parser = subparsers.add_parser("shares", help="Share operations")
    shares_subparsers = shares_parser.add_subparsers(dest="subcommand", help="Share commands")

    # Shares: create
    shares_create = shares_subparsers.add_parser("create", help="Create a share link")
    shares_create.add_argument("--document-id", required=True, help="Document ID")
    shares_create.add_argument("--unpublished", action="store_true", help="Create as unpublished")

    # Shares: list
    shares_list = shares_subparsers.add_parser("list", help="List share links")
    shares_list.add_argument("--document-id", help="Filter by document ID")
    shares_list.add_argument("--limit", type=int, default=25, help="Number of shares to return")
    shares_list.add_argument("--offset", type=int, default=0, help="Pagination offset")

    # Shares: info
    shares_info = shares_subparsers.add_parser("info", help="Get share information")
    shares_info.add_argument("--id", required=True, help="Share ID")

    # Shares: revoke
    shares_revoke = shares_subparsers.add_parser("revoke", help="Revoke a share link")
    shares_revoke.add_argument("--id", required=True, help="Share ID")

    # Shares: update
    shares_update = shares_subparsers.add_parser("update", help="Update a share link")
    shares_update.add_argument("--id", required=True, help="Share ID")
    shares_update.add_argument("--published", action="store_true", help="Set share as published")

    # Stars subcommand
    stars_parser = subparsers.add_parser("stars", help="Star (favorite) operations")
    stars_subparsers = stars_parser.add_subparsers(dest="subcommand", help="Star commands")

    # Stars: create
    stars_create = stars_subparsers.add_parser("create", help="Star a document")
    stars_create.add_argument("--document-id", required=True, help="Document ID")

    # Stars: list
    stars_list = stars_subparsers.add_parser("list", help="List starred documents")
    stars_list.add_argument("--limit", type=int, default=25, help="Number of stars to return")
    stars_list.add_argument("--offset", type=int, default=0, help="Pagination offset")

    # Stars: delete
    stars_delete = stars_subparsers.add_parser("delete", help="Unstar a document")
    stars_delete.add_argument("--id", required=True, help="Star ID")

    # Stars: update
    stars_update = stars_subparsers.add_parser("update", help="Update a star's position")
    stars_update.add_argument("--id", required=True, help="Star ID")
    stars_update.add_argument("--index", required=True, help="New index/position")

    # Views subcommand
    views_parser = subparsers.add_parser("views", help="Document view operations")
    views_subparsers = views_parser.add_subparsers(dest="subcommand", help="View commands")

    # Views: create
    views_create = views_subparsers.add_parser("create", help="Create a view record for a document")
    views_create.add_argument("--document-id", required=True, help="Document ID")

    # Views: list
    views_list = views_subparsers.add_parser("list", help="List views for a document")
    views_list.add_argument("--document-id", required=True, help="Document ID")
    views_list.add_argument("--limit", type=int, default=25, help="Number of views to return")
    views_list.add_argument("--offset", type=int, default=0, help="Pagination offset")

    # Revisions subcommand
    revisions_parser = subparsers.add_parser("revisions", help="Document revision operations")
    revisions_subparsers = revisions_parser.add_subparsers(dest="subcommand", help="Revision commands")

    # Revisions: list
    revisions_list = revisions_subparsers.add_parser("list", help="List document revisions")
    revisions_list.add_argument("--document-id", required=True, help="Document ID")
    revisions_list.add_argument("--limit", type=int, default=25, help="Number of revisions to return")
    revisions_list.add_argument("--offset", type=int, default=0, help="Pagination offset")

    # Revisions: info
    revisions_info = revisions_subparsers.add_parser("info", help="Get revision information")
    revisions_info.add_argument("--id", required=True, help="Revision ID")

    # Events subcommand
    events_parser = subparsers.add_parser("events", help="Event log operations")
    events_subparsers = events_parser.add_subparsers(dest="subcommand", help="Event commands")

    # Events: list
    events_list = events_subparsers.add_parser("list", help="List events (audit log)")
    events_list.add_argument("--name", help="Filter by event name")
    events_list.add_argument("--actor-id", help="Filter by actor (user) ID")
    events_list.add_argument("--document-id", help="Filter by document ID")
    events_list.add_argument("--collection-id", help="Filter by collection ID")
    events_list.add_argument("--limit", type=int, default=25, help="Number of events to return")
    events_list.add_argument("--offset", type=int, default=0, help="Pagination offset")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize client
    try:
        client = OutlineClient(api_key=args.api_key, base_url=args.base_url, timeout=args.timeout)
    except OutlineAPIError as e:
        print(f"Error initializing client: {e}", file=sys.stderr)
        return 1

    # Route to appropriate handler
    if args.command in ["documents", "docs", "doc"]:
        if not args.subcommand:
            docs_parser.print_help()
            return 1

        doc_commands: dict[str, CommandHandler] = {
            "create": create_document,
            "info": get_document,
            "list": list_documents,
            "update": update_document,
            "delete": delete_document,
            "archive": archive_document,
            "restore": restore_document,
            "move": move_document,
            "duplicate": duplicate_document,
            "templatize": templatize_document,
            "export": export_document,
            "import": import_document,
            "drafts": list_drafts,
            "archived": list_archived_documents,
            "deleted": list_deleted_documents,
            "viewed": list_viewed_documents,
            "empty-trash": empty_trash,
            "unpublish": unpublish_document,
            "add-user": add_user_to_document,
            "remove-user": remove_user_from_document,
            "memberships": list_document_memberships,
            "users": list_document_users,
            "add-group": add_group_to_document,
            "remove-group": remove_group_from_document,
            "group-memberships": list_document_group_memberships,
        }
        return doc_commands[args.subcommand](client, args)

    elif args.command in ["collections", "colls", "coll"]:
        if not args.subcommand:
            colls_parser.print_help()
            return 1

        coll_commands: dict[str, CommandHandler] = {
            "list": list_collections,
            "info": get_collection,
            "create": create_collection,
            "update": update_collection,
            "delete": delete_collection,
            "documents": list_collection_documents,
            "add-user": add_user_to_collection,
            "remove-user": remove_user_from_collection,
            "memberships": list_collection_memberships,
            "add-group": add_group_to_collection,
            "remove-group": remove_group_from_collection,
            "group-memberships": list_collection_group_memberships,
            "export": export_collection,
            "export-all": export_all_collections,
        }
        return coll_commands[args.subcommand](client, args)

    elif args.command == "search":
        return search_documents(client, args)

    elif args.command == "auth":
        if not args.subcommand:
            auth_parser.print_help()
            return 1

        auth_commands: dict[str, CommandHandler] = {
            "info": get_auth_info,
        }
        return auth_commands[args.subcommand](client, args)

    elif args.command == "users":
        if not args.subcommand:
            users_parser.print_help()
            return 1

        user_commands: dict[str, CommandHandler] = {
            "list": list_users,
            "info": get_user,
            "invite": invite_user,
            "update": update_user,
            "update-role": update_user_role,
            "suspend": suspend_user,
            "activate": activate_user,
            "delete": delete_user,
        }
        return user_commands[args.subcommand](client, args)

    elif args.command == "groups":
        if not args.subcommand:
            groups_parser.print_help()
            return 1

        group_commands: dict[str, CommandHandler] = {
            "list": list_groups,
            "info": get_group,
            "create": create_group,
            "update": update_group,
            "delete": delete_group,
            "add-user": add_user_to_group,
            "remove-user": remove_user_from_group,
            "memberships": list_group_memberships,
        }
        return group_commands[args.subcommand](client, args)

    elif args.command in ["file-operations", "fileops"]:
        if not args.subcommand:
            file_ops_parser.print_help()
            return 1

        file_ops_commands: dict[str, CommandHandler] = {
            "list": list_file_operations,
            "info": get_file_operation,
            "redirect": redirect_file_operation,
            "delete": delete_file_operation,
        }
        return file_ops_commands[args.subcommand](client, args)

    elif args.command == "comments":
        if not args.subcommand:
            comments_parser.print_help()
            return 1

        comment_commands: dict[str, CommandHandler] = {
            "list": list_comments,
            "info": get_comment,
            "create": create_comment,
            "update": update_comment,
            "delete": delete_comment,
            "resolve": resolve_comment,
            "unresolve": unresolve_comment,
            "add-reaction": add_comment_reaction,
            "remove-reaction": remove_comment_reaction,
        }
        return comment_commands[args.subcommand](client, args)

    elif args.command == "attachments":
        if not args.subcommand:
            attachments_parser.print_help()
            return 1

        attachment_commands: dict[str, CommandHandler] = {
            "create": create_attachment,
            "delete": delete_attachment,
            "redirect": redirect_attachment,
        }
        return attachment_commands[args.subcommand](client, args)

    elif args.command == "shares":
        if not args.subcommand:
            shares_parser.print_help()
            return 1

        share_commands: dict[str, CommandHandler] = {
            "create": create_share,
            "list": list_shares,
            "info": get_share,
            "revoke": revoke_share,
            "update": update_share,
        }
        return share_commands[args.subcommand](client, args)

    elif args.command == "stars":
        if not args.subcommand:
            stars_parser.print_help()
            return 1

        star_commands: dict[str, CommandHandler] = {
            "create": create_star,
            "list": list_stars,
            "delete": delete_star,
            "update": update_star,
        }
        return star_commands[args.subcommand](client, args)

    elif args.command == "views":
        if not args.subcommand:
            views_parser.print_help()
            return 1

        view_commands: dict[str, CommandHandler] = {
            "create": create_view,
            "list": list_views,
        }
        return view_commands[args.subcommand](client, args)

    elif args.command == "revisions":
        if not args.subcommand:
            revisions_parser.print_help()
            return 1

        revision_commands: dict[str, CommandHandler] = {
            "list": list_revisions,
            "info": get_revision,
        }
        return revision_commands[args.subcommand](client, args)

    elif args.command == "events":
        if not args.subcommand:
            events_parser.print_help()
            return 1

        event_commands: dict[str, CommandHandler] = {
            "list": list_events,
        }
        return event_commands[args.subcommand](client, args)

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
