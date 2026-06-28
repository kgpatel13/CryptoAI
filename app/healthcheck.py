from __future__ import annotations


def healthcheck() -> dict:
    return {
        "status": "ok",
        "service": "CryptoAI",
        "mode": "paper",
        "live_trading": "disabled",
    }


if __name__ == "__main__":
    print(healthcheck())
