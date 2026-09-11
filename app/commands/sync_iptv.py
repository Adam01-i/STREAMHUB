import asyncio

from app.services.iptv_org.sync import run_full_sync


def print_report(report: dict) -> None:
    print("=================================")
    print(" IPTV-ORG SYNCHRONIZATION")
    print("=================================")
    for key, value in report.items():
        print(f"{key}: {value}")
    print("=================================")
    print("Synchronization completed.")


async def main() -> None:
    report = await run_full_sync()
    print_report(report)


if __name__ == "__main__":
    asyncio.run(main())
