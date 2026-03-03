#!/usr/bin/env node
/**
 * trend-mixer-cli (JavaScript版)
 *
 * 使い方:
 *   node src/main.js --demo
 *   node src/main.js --trend "名前|課題|実装方針" --trend "名前|課題|実装方針"
 */

const IDEA_PATTERNS = [
  {
    name: "速報ウォッチャー",
    catch: "ニュースを読むだけで、次にやることが決まる",
    output: "話題の更新通知 + 優先度つきTODO",
  },
  {
    name: "リスク見える化メモ",
    catch: "難しいセキュリティ情報を1枚で理解",
    output: "危険度ラベル付きの要約カード",
  },
  {
    name: "学習スタートキット",
    catch: "トレンドを学習タスクへ変換",
    output: "30分で試せるハンズオン手順",
  },
];

function parseArgs(argv) {
  const args = {
    trends: [],
    pattern: 0,
    demo: false,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];

    if (token === "--demo") {
      args.demo = true;
      continue;
    }

    if (token === "--pattern") {
      const value = argv[i + 1];
      if (!value) throw new Error("--pattern の値がありません。");
      args.pattern = Number(value);
      i += 1;
      continue;
    }

    if (token === "--trend") {
      const value = argv[i + 1];
      if (!value) throw new Error("--trend の値がありません。");
      args.trends.push(value);
      i += 1;
      continue;
    }

    throw new Error(`不明な引数です: ${token}`);
  }

  return args;
}

function parseTrends(rawTrends) {
  return rawTrends.map((item) => {
    const parts = item.split("|").map((x) => x.trim());
    if (parts.length !== 3) {
      throw new Error("トレンドは '名前|解決したい課題|実装の方向性' 形式で指定してください。");
    }

    return {
      name: parts[0],
      problem: parts[1],
      approach: parts[2],
    };
  });
}

function buildIdea(trends, patternIndex = 0) {
  if (trends.length < 2) {
    throw new Error("最低2つのトレンドを入力してください。");
  }

  const pattern = IDEA_PATTERNS[patternIndex % IDEA_PATTERNS.length];
  const combo = trends.map((t) => t.name).join(" + ");
  const approaches = trends.map((t) => t.approach).join(" / ");

  return [
    `システム名: ${pattern.name}`,
    `キャッチコピー: ${pattern.catch}`,
    "",
    "1) どんな課題を解く？",
    `- ${trends[0].problem}`,
    `- ${trends[1].problem}`,
    "",
    "2) どう組み合わせる？",
    `- 掛け合わせ: ${combo}`,
    `- 実装方針: ${approaches}`,
    "",
    "3) 何が出力される？",
    `- ${pattern.output}`,
    "",
    "4) 最小実装（1〜3時間）",
    "- JSONまたはCSVでトピックを読み込む",
    "- 重要語でタグ付けして優先順位を決める",
    "- Markdown形式で結果を保存する",
  ].join("\n");
}

function main() {
  try {
    const args = parseArgs(process.argv.slice(2));

    const trends = args.demo
      ? [
          {
            name: "TypeScript/JavaScript開発の継続人気",
            problem: "新しいツールが多く、どれから触るべきか迷う",
            approach: "用途別の比較メモを自動生成する",
          },
          {
            name: "セキュリティ注意喚起の増加",
            problem: "脆弱性情報が難しく、対応優先度が決めにくい",
            approach: "危険度と対応期限で並べ替える",
          },
        ]
      : parseTrends(args.trends);

    console.log("Trend Mixer CLI v2.0 (JavaScript)");
    console.log("=".repeat(42));
    console.log(buildIdea(trends, args.pattern));
  } catch (err) {
    console.error("エラー:", err.message);
    console.error("\n使い方:");
    console.error("  node src/main.js --demo");
    console.error("  node src/main.js --trend \"名前|課題|実装方針\" --trend \"名前|課題|実装方針\"");
    process.exit(1);
  }
}

main();
