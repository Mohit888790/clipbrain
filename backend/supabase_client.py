"""Supabase client for REST API and database operations."""

import httpx
from typing import Any
from config import settings


class SupabaseClient:
    """Client for interacting with Supabase REST API."""
    
    def __init__(self):
        self.base_url = f"{settings.supabase_url}/rest/v1"
        self.headers = {
            "apikey": settings.supabase_service_key,
            "Authorization": f"Bearer {settings.supabase_service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def select(
        self, 
        table: str, 
        columns: str = "*",
        filters: dict[str, Any] | None = None,
        order: str | None = None,
        limit: int | None = None
    ) -> list[dict]:
        """
        Select rows from a table.
        
        Args:
            table: Table name
            columns: Columns to select (default: *)
            filters: Dictionary of column:value filters
            order: Order by clause (e.g., "created_at.desc")
            limit: Maximum number of rows to return
        
        Returns:
            List of rows as dictionaries
        """
        url = f"{self.base_url}/{table}"
        params = {"select": columns}
        
        if filters:
            for key, value in filters.items():
                params[key] = f"eq.{value}"
        
        if order:
            params["order"] = order
        
        if limit:
            params["limit"] = str(limit)
        
        response = await self.client.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    async def insert(self, table: str, data: dict | list[dict]) -> list[dict]:
        """
        Insert row(s) into a table.
        
        Args:
            table: Table name
            data: Dictionary or list of dictionaries to insert
        
        Returns:
            Inserted row(s)
        """
        url = f"{self.base_url}/{table}"
        response = await self.client.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    async def update(
        self, 
        table: str, 
        data: dict,
        filters: dict[str, Any]
    ) -> list[dict]:
        """
        Update rows in a table.
        
        Args:
            table: Table name
            data: Dictionary of columns to update
            filters: Dictionary of column:value filters
        
        Returns:
            Updated row(s)
        """
        url = f"{self.base_url}/{table}"
        params = {}
        
        for key, value in filters.items():
            params[key] = f"eq.{value}"
        
        response = await self.client.patch(
            url, 
            headers=self.headers, 
            params=params,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    async def delete(self, table: str, filters: dict[str, Any]) -> None:
        """
        Delete rows from a table.
        
        Args:
            table: Table name
            filters: Dictionary of column:value filters
        """
        url = f"{self.base_url}/{table}"
        params = {}
        
        for key, value in filters.items():
            params[key] = f"eq.{value}"
        
        response = await self.client.delete(url, headers=self.headers, params=params)
        response.raise_for_status()
    
    async def rpc(self, function_name: str, params: dict | None = None) -> Any:
        """
        Call a PostgreSQL function via RPC.
        
        Args:
            function_name: Name of the function to call
            params: Parameters to pass to the function
        
        Returns:
            Function result
        """
        url = f"{self.base_url}/rpc/{function_name}"
        response = await self.client.post(
            url, 
            headers=self.headers,
            json=params or {}
        )
        response.raise_for_status()
        return response.json()


# Global Supabase client instance
supabase = SupabaseClient()
