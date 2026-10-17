#!/usr/bin/env python3
"""Add a `publish_carousel` tool to jlbadano/ig-mcp (MIT) and switch off DMs.

Run inside your clone of https://github.com/jlbadano/ig-mcp :
    python3 add_carousel.py
Changes:
  1. InstagramClient.publish_carousel(image_urls, caption): uploads 2–10 public image URLs
     as carousel items, waits until Instagram has processed them, then publishes.
  2. A `publish_carousel` MCP tool that calls it.
  3. Removes the send_dm tool, so the server can only post, not message people.
Safe to run twice."""
import pathlib, re, sys

root = pathlib.Path(".")
client = root / "src/instagram_client.py"
server = root / "src/instagram_mcp_server.py"
if not client.exists() or not server.exists():
    sys.exit("Run this from the ig-mcp folder (src/instagram_client.py not found).")

c = client.read_text()
if "async def publish_carousel" not in c:
    method = '''
    async def publish_carousel(self, image_urls: List[str], caption: str = "") -> Dict[str, Any]:
        """Publish 2-10 public image URLs as one carousel post (Graph API CAROUSEL container)."""
        import asyncio
        account_id = self.settings.instagram_business_account_id
        if not account_id:
            raise InstagramAPIError("Instagram business account ID not configured")
        if not 2 <= len(image_urls) <= 10:
            raise InstagramAPIError("A carousel needs between 2 and 10 images")
        if caption and len(caption) > 2200:
            raise InstagramAPIError("Caption must be 2200 characters or less")

        async def wait_ready(container_id: str) -> None:
            for _ in range(30):
                status = await self._make_request(
                    "GET", container_id, params={"fields": "status_code"}, use_cache=False
                )
                code = status.get("status_code")
                if code == "FINISHED":
                    return
                if code in ("ERROR", "EXPIRED"):
                    raise InstagramAPIError(f"Instagram could not process media {container_id}: {code}")
                await asyncio.sleep(2)
            raise InstagramAPIError(f"Timed out waiting for media {container_id}")

        children = []
        for url in image_urls:
            await self._validate_image_aspect_ratio(str(url))
            item = await self._make_request(
                "POST", f"{account_id}/media",
                data={"image_url": str(url), "is_carousel_item": "true"},
            )
            await wait_ready(item["id"])
            children.append(item["id"])

        container = await self._make_request(
            "POST", f"{account_id}/media",
            data={"media_type": "CAROUSEL", "children": ",".join(children), "caption": caption or ""},
        )
        await wait_ready(container["id"])
        published = await self._make_request(
            "POST", f"{account_id}/media_publish", data={"creation_id": container["id"]}
        )
        return {"id": published["id"], "children": children, "success": True}
'''
    anchor = "    async def get_account_pages(self)"
    c = c.replace(anchor, method.lstrip("\n") + "\n" + anchor, 1)
    client.write_text(c)
    print("client: publish_carousel added")

s = server.read_text()
if 'name="publish_carousel"' not in s:
    tool = '''                Tool(
                    name="publish_carousel",
                    description=(
                        "Publish 2-10 images as one Instagram carousel post. "
                        "Images must be public URLs (e.g. GitHub Pages), JPEG or PNG, "
                        "aspect ratio between 4:5 and 1.91:1."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "image_urls": {
                                "type": "array",
                                "items": {"type": "string", "format": "uri"},
                                "minItems": 2,
                                "maxItems": 10,
                                "description": "Public image URLs in slide order",
                            },
                            "caption": {"type": "string", "description": "Post caption, max 2200 characters"},
                        },
                        "required": ["image_urls"],
                    },
                ),
'''
    s = s.replace('                Tool(\n                    name="get_account_pages",', tool + '                Tool(\n                    name="get_account_pages",', 1)
    handler = '''                elif name == "publish_carousel":
                    data = await instagram_client.publish_carousel(
                        arguments["image_urls"], arguments.get("caption", "")
                    )
                    result = MCPToolResult(
                        success=True,
                        data=data,
                        metadata={"tool": name, "timestamp": datetime.utcnow().isoformat()},
                    )

'''
    s = s.replace('                elif name == "get_account_pages":', handler + '                elif name == "get_account_pages":', 1)
    print("server: publish_carousel tool added")

# remove the send_dm tool definition so the server cannot message people
m = re.search(r'\n                Tool\(\n                    name="send_dm",.*?\n                \),', s, re.S)
if m:
    s = s.replace(m.group(0), "", 1)
    print("server: send_dm tool removed")
server.write_text(s)
print("done")
