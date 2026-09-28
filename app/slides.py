"""Banner slides. One table (hero_slides) feeds both the homepage slider
(page = 'home': picture only, text is inside the image) and the Services
page banner (page = 'services': picture + heading + text)."""
import logging

from app.supabase_client import supabase_admin

logger = logging.getLogger("minait")


def page_slides(page: str, active_only: bool = False) -> list[dict] | None:
    """Slides for one page, in order. Before db/schema.sql adds the `page`
    column every slide is a homepage slide, so 'home' falls back to all
    slides and other pages get None ("not available yet")."""
    def query():
        q = supabase_admin().table("hero_slides").select("*")
        return q.eq("is_active", True) if active_only else q

    try:
        return query().eq("page", page).order("sort_order").order("id").execute().data
    except Exception:
        logger.exception("Loading %s slides by page failed", page)
        if page != "home":
            return None
        return query().order("sort_order").order("id").execute().data
