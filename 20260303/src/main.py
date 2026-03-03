#!/usr/bin/env python3
"""Trend Mixer

過去24時間のトレンドを2〜3個入力すると、
小さく作れるシステム案を自動で提案するCLIです。
"""

from __future__ import annotations

from dataclasses import dataclass
from textwrap import dedent
import argparse


@dataclass
class Trend:
    name: str
    problem: str
    approach: str


IDEA_PATTERNS = [
    {
        "name": "速報ウォッチャー",
        "catch": "ニュースを読むだけで、次にやることが決まる",
        "output": "話題の更新通知 + 優先度つきTODO",
    },
    {
        "name": "リスク見える化メモ",
        "catch": "難しいセキュリティ情報を1枚で理解",
        "output": "危険度ラベル付きの要約カード",
    },
    {
        "name": "学習スタートキット",
        "catch": "トレンドを学習タスクへ変換",
        "output": "30分で試せるハンズオン手順",
    },
]


def build_idea(trends: list[Trend], pattern_index: int = 0) -> str:
    if len(trends) < 2:
        raise ValueError("最低2つのトレンドを入力してください。")

    pattern = IDEA_PATTERNS[pattern_index % len(IDEA_PATTERNS)]
    combo = " + ".join(t.name for t in trends)

    summary = dedent(
        f"""
        システム名: {pattern['name']}
        キャッチコピー: {pattern['catch']}

        1) どんな課題を解く？
        - {trends[0].problem}
        - {trends[1].problem}

        2) どう組み合わせる？
        - 掛け合わせ: {combo}
        - 実装方針: {' / '.join(t.approach for t in trends)}

        3) 何が出力される？
        - {pattern['output']}

        4) 最小実装（1〜3時間）
        - JSONまたはCSVでトピックを読み込む
        - 重要語でタグ付けして優先順位を決める
        - Markdown形式で結果を保存する
        """
    ).strip()

    return summary


def parse_trends(raw_items: list[str]) -> list[Trend]:
    trends: list[Trend] = []
    for item in raw_items:
        parts = [p.strip() for p in item.split("|")]
        if len(parts) != 3:
            raise ValueError(
                "トレンドは '名前|解決したい課題|実装の方向性' 形式で指定してください。"
            )
        trends.append(Trend(name=parts[0], problem=parts[1], approach=parts[2]))
    return trends


def main() -> int:
    parser = argparse.ArgumentParser(
        description="トレンドを掛け合わせて、初学者向けシステム案を提案するツール"
    )
    parser.add_argument(
        "--trend",
        action="append",
        default=[],
        help="形式: 名前|解決したい課題|実装の方向性（最低2つ指定）",
    )
    parser.add_argument("--pattern", type=int, default=0, help="提案パターン番号")
    parser.add_argument("--demo", action="store_true", help="デモ入力で実行")
    args = parser.parse_args()

    if args.demo:
        trends = [
            Trend(
                name="AIエージェント運用",
                problem="ツールが増えて何を優先導入すべきか判断しづらい",
                approach="更新情報を日次で集約して、用途別に分類する",
            ),
            Trend(
                name="セキュリティ注意喚起",
                problem="脆弱性情報が難しく、対応が後回しになりやすい",
                approach="危険度に応じて、対応期限つきで一覧化する",
            ),
        ]
    else:
        trends = parse_trends(args.trend)

    print("Trend Mixer v1.0")
    print("=" * 40)
    print(build_idea(trends, args.pattern))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
