from datetime import datetime, timezone

from app.core.database import AsyncSessionLocal
from app.models.enums import SyncStatus
from app.models.sync import SyncRun
from app.services.iptv_org.client import IptvOrgClient
from app.services.iptv_org.importer import (
    import_channels,
    import_epg,
    import_feeds,
    import_reference_data,
    import_streams,
)


async def run_full_sync() -> dict:
    async with AsyncSessionLocal() as session:
        sync_run = SyncRun(status=SyncStatus.RUNNING)
        session.add(sync_run)
        await session.commit()
        await session.refresh(sync_run)

        client = IptvOrgClient()
        try:
            await import_reference_data(session, client)
            channel_report = await import_channels(session, client)
            feeds_count = await import_feeds(session, client)
            streams_count = await import_streams(session, client)
            epg_report = await import_epg(session, client)

            report = {
                **channel_report,
                "feeds_imported": feeds_count,
                "streams_imported": streams_count if streams_count is not None else 0,
                **epg_report,
            }

            sync_run.status = SyncStatus.SUCCESS
            sync_run.channels_imported = channel_report["channels_imported"]
            sync_run.channels_updated = channel_report["channels_updated"]
            sync_run.streams_imported = streams_count if streams_count is not None else 0
            sync_run.report_json = report
        except Exception as exc:
            sync_run.status = SyncStatus.FAILED
            sync_run.report_json = {"error": str(exc)}
            raise
        finally:
            sync_run.finished_at = datetime.now(timezone.utc)
            await session.commit()
            await client.aclose()

        return sync_run.report_json