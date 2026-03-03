// KEV-Watch: CISA Known Exploited Vulnerabilities リアルタイム監視CLI
// 作成: 2026-03-03
// トレンド背景:
//   - Go言語がAIエージェント・システムツール開発で急浮上 (HN: "A case for Go as the best language for AI agents")
//   - Android 129件CVEパッチ・Cisco CVSS 10.0・APT28 MSHTML悪用と既知悪用脆弱性が急増
//   - CLIツール文化の盛り上がり (HN: Pianoterm, GitHub Trending: Crush)
// 実行: go run src/main.go

package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"net/http"
	"os"
	"sort"
	"strings"
	"time"
)

// CISA KEVカタログのエンドポイント（公式・無料・APIキー不要）
const kevURL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

// ANSIカラーコード
const (
	colorReset  = "\033[0m"
	colorRed    = "\033[31m"
	colorYellow = "\033[33m"
	colorGreen  = "\033[32m"
	colorCyan   = "\033[36m"
	colorBold   = "\033[1m"
	colorDim    = "\033[2m"
)

// KEVCatalog はCISAのKEVカタログJSON全体を表す
type KEVCatalog struct {
	Title           string          `json:"title"`
	CatalogVersion  string          `json:"catalogVersion"`
	DateReleased    string          `json:"dateReleased"`
	Count           int             `json:"count"`
	Vulnerabilities []Vulnerability `json:"vulnerabilities"`
}

// Vulnerability はKEVカタログ内の1件の脆弱性エントリを表す
type Vulnerability struct {
	CveID             string `json:"cveID"`
	VendorProject     string `json:"vendorProject"`
	Product           string `json:"product"`
	VulnerabilityName string `json:"vulnerabilityName"`
	DateAdded         string `json:"dateAdded"`
	ShortDescription  string `json:"shortDescription"`
	RequiredAction    string `json:"requiredAction"`
	DueDate           string `json:"dueDate"`
	Notes             string `json:"notes"`
}

// vendorStat はベンダー別CVE件数の集計に使う
type vendorStat struct {
	name  string
	count int
}

// sampleJSON は2026-03-03時点の実際のセキュリティニュースに基づくサンプルデータ
// ネットワーク接続なし/フォールバック時に使用
var sampleJSON = `{
  "title": "CISA Known Exploited Vulnerabilities Catalog [SAMPLE - 2026-03-03]",
  "catalogVersion": "2026.03.03",
  "dateReleased": "2026-03-03T00:00:00.000Z",
  "count": 1247,
  "vulnerabilities": [
    {
      "cveID": "CVE-2026-20127",
      "vendorProject": "Cisco",
      "product": "Catalyst SD-WAN Controller",
      "vulnerabilityName": "Cisco Catalyst SD-WAN Authentication Bypass Vulnerability",
      "dateAdded": "2026-03-03",
      "shortDescription": "Cisco Catalyst SD-WAN Controller and SD-WAN Manager contain an authentication bypass vulnerability allowing an unauthenticated remote attacker to bypass authentication. CVSS score 10.0.",
      "requiredAction": "Apply mitigations per vendor instructions or discontinue use of the product if mitigations are unavailable.",
      "dueDate": "2026-03-24",
      "notes": "CVSS 10.0 - Actively exploited in the wild."
    },
    {
      "cveID": "CVE-2026-21385",
      "vendorProject": "Google",
      "product": "Android (Qualcomm Display Driver)",
      "vulnerabilityName": "Qualcomm Display Driver Integer Overflow Vulnerability",
      "dateAdded": "2026-03-03",
      "shortDescription": "An integer overflow or wraparound bug in the Qualcomm Display component of Android causes memory corruption during memory allocation alignment. Actively exploited in limited, targeted attacks.",
      "requiredAction": "Apply Android March 2026 security update (patch level 2026-03-05).",
      "dueDate": "2026-03-24",
      "notes": "Zero-day confirmed by Google and Qualcomm. Reported by Android Security team on 2025-12-18."
    },
    {
      "cveID": "CVE-2026-0006",
      "vendorProject": "Google",
      "product": "Android System Component",
      "vulnerabilityName": "Android System Remote Code Execution Vulnerability",
      "dateAdded": "2026-03-03",
      "shortDescription": "A critical flaw in the Android System component could lead to remote code execution without requiring any additional execution privileges or user interaction.",
      "requiredAction": "Apply Android March 2026 security update.",
      "dueDate": "2026-03-24",
      "notes": "Part of the 129-CVE March 2026 Android Security Bulletin."
    },
    {
      "cveID": "CVE-2026-21513",
      "vendorProject": "Microsoft",
      "product": "MSHTML",
      "vulnerabilityName": "Microsoft MSHTML Security Feature Bypass Vulnerability",
      "dateAdded": "2026-02-20",
      "shortDescription": "A high-severity MSHTML security feature bypass (CVSS 8.8) exploited by APT28 (Russia-linked threat actor) before Microsoft's February 2026 Patch Tuesday.",
      "requiredAction": "Apply Microsoft February 2026 Patch Tuesday updates.",
      "dueDate": "2026-03-13",
      "notes": "Tied to APT28. Patched in February 2026 Patch Tuesday."
    },
    {
      "cveID": "CVE-2026-0047",
      "vendorProject": "Google",
      "product": "Android Framework",
      "vulnerabilityName": "Android Framework Privilege Escalation Vulnerability",
      "dateAdded": "2026-03-03",
      "shortDescription": "A privilege escalation vulnerability in the Android Framework component allows an attacker to gain elevated privileges.",
      "requiredAction": "Apply Android March 2026 security update.",
      "dueDate": "2026-03-24",
      "notes": "Part of March 2026 Android Security Bulletin."
    },
    {
      "cveID": "CVE-2025-48631",
      "vendorProject": "Google",
      "product": "Android System",
      "vulnerabilityName": "Android System Denial of Service Vulnerability",
      "dateAdded": "2026-03-03",
      "shortDescription": "A denial-of-service (DoS) vulnerability in the Android System component.",
      "requiredAction": "Apply Android March 2026 security update.",
      "dueDate": "2026-03-24",
      "notes": "Part of March 2026 Android Security Bulletin."
    },
    {
      "cveID": "CVE-2025-21298",
      "vendorProject": "Microsoft",
      "product": "Windows OLE",
      "vulnerabilityName": "Windows OLE Remote Code Execution Vulnerability",
      "dateAdded": "2026-02-11",
      "shortDescription": "A zero-click RCE vulnerability in Windows OLE triggered by opening a specially crafted email in Outlook.",
      "requiredAction": "Apply Microsoft February 2026 Patch Tuesday updates.",
      "dueDate": "2026-03-04",
      "notes": "Zero-click, rated Critical."
    },
    {
      "cveID": "CVE-2025-29824",
      "vendorProject": "Microsoft",
      "product": "Windows Common Log File System Driver",
      "vulnerabilityName": "Windows CLFS Privilege Escalation Vulnerability",
      "dateAdded": "2026-02-11",
      "shortDescription": "Use-after-free in Windows Common Log File System Driver allows local privilege escalation to SYSTEM.",
      "requiredAction": "Apply Microsoft February 2026 Patch Tuesday updates.",
      "dueDate": "2026-03-04",
      "notes": "Actively exploited by ransomware groups."
    },
    {
      "cveID": "CVE-2026-1234",
      "vendorProject": "Fortinet",
      "product": "FortiOS",
      "vulnerabilityName": "FortiOS Path Traversal Remote Code Execution",
      "dateAdded": "2026-02-28",
      "shortDescription": "A path traversal vulnerability in FortiOS SSL VPN allows unauthenticated remote attackers to read and execute arbitrary files via crafted HTTP requests.",
      "requiredAction": "Apply vendor-supplied patches or restrict access to SSL VPN management interface.",
      "dueDate": "2026-03-21",
      "notes": "Actively exploited."
    },
    {
      "cveID": "CVE-2025-44228",
      "vendorProject": "Apache",
      "product": "Log4j",
      "vulnerabilityName": "Apache Log4j2 JNDI Injection Vulnerability (Log4Shell successor)",
      "dateAdded": "2026-01-15",
      "shortDescription": "A new JNDI injection vector in Apache Log4j2 variants allows remote code execution in misconfigured deployments.",
      "requiredAction": "Upgrade Log4j2 to latest version and disable JNDI lookup features.",
      "dueDate": "2026-02-05",
      "notes": ""
    },
    {
      "cveID": "CVE-2025-0678",
      "vendorProject": "Palo Alto Networks",
      "product": "PAN-OS",
      "vulnerabilityName": "PAN-OS Command Injection in GlobalProtect Gateway",
      "dateAdded": "2026-02-05",
      "shortDescription": "An OS command injection vulnerability in the GlobalProtect Gateway of Palo Alto Networks PAN-OS allows an unauthenticated remote attacker to execute arbitrary commands.",
      "requiredAction": "Apply hotfix from Palo Alto Networks.",
      "dueDate": "2026-02-26",
      "notes": "Mass exploitation observed."
    },
    {
      "cveID": "CVE-2024-55591",
      "vendorProject": "Fortinet",
      "product": "FortiOS / FortiProxy",
      "vulnerabilityName": "Fortinet FortiOS and FortiProxy Authentication Bypass",
      "dateAdded": "2025-12-10",
      "shortDescription": "An authentication bypass vulnerability using an alternate path or channel in FortiOS and FortiProxy allows an unauthenticated remote attacker to gain super-admin privileges.",
      "requiredAction": "Apply updates per vendor advisory.",
      "dueDate": "2025-12-31",
      "notes": ""
    }
  ]
}`

func main() {
	days := flag.Int("days", 30, "直近N日以内に追加されたCVEを表示")
	vendor := flag.String("vendor", "", "ベンダー/プロジェクト名でフィルタ（部分一致・大文字小文字無視）")
	detail := flag.Bool("detail", false, "詳細説明・対応アクション・期限を表示")
	offline := flag.Bool("offline", false, "オフラインモード（内蔵サンプルデータを使用）")
	flag.Parse()

	printHeader()

	var catalog *KEVCatalog
	var err error
	var dataSource string

	if *offline {
		catalog, err = loadSampleData()
		dataSource = "内蔵サンプルデータ (2026-03-03)"
	} else {
		fmt.Printf("  %sCISAカタログを取得中...%s\n", colorYellow, colorReset)
		catalog, err = fetchKEV()
		if err != nil {
			fmt.Printf("  %s[WARN] ライブデータ取得失敗: %v%s\n", colorYellow, err, colorReset)
			fmt.Printf("  %sサンプルデータにフォールバック中...%s\n\n", colorDim, colorReset)
			catalog, err = loadSampleData()
			dataSource = "内蔵サンプルデータ (2026-03-03 ニュースに基づく)"
		} else {
			dataSource = "CISA ライブデータ"
		}
	}

	if err != nil {
		fmt.Fprintf(os.Stderr, "  %s[ERROR] データ読み込み失敗: %v%s\n", colorRed, err, colorReset)
		os.Exit(1)
	}

	fmt.Printf("  %sデータソース: %s%s\n\n", colorDim, dataSource, colorReset)

	cutoff := time.Now().AddDate(0, 0, -*days)
	recent := filterVulns(catalog.Vulnerabilities, cutoff, *vendor)

	// 日付降順でソート（最新が先頭）
	sort.Slice(recent, func(i, j int) bool {
		return recent[i].DateAdded > recent[j].DateAdded
	})

	printSummary(catalog, recent, *days, *vendor)

	if len(recent) == 0 {
		fmt.Printf("  %s該当するCVEが見つかりませんでした。%s\n", colorYellow, colorReset)
		return
	}

	printVulnList(recent, *detail)
	printVendorStats(recent, *days)
	printFooter(len(recent), *days)
}

// printHeader はバナーを表示する
func printHeader() {
	fmt.Printf("\n%s%s╔══════════════════════════════════════════════════════╗%s\n", colorBold, colorCyan, colorReset)
	fmt.Printf("%s%s║  KEV-Watch — CISA 既知悪用脆弱性リアルタイム監視 CLI  ║%s\n", colorBold, colorCyan, colorReset)
	fmt.Printf("%s%s╚══════════════════════════════════════════════════════╝%s\n", colorBold, colorCyan, colorReset)
	fmt.Printf("%s  Built with Go 1.24 | Trend: 2026-03-03%s\n\n", colorDim, colorReset)
}

// printSummary はカタログのサマリーを表示する
func printSummary(catalog *KEVCatalog, recent []Vulnerability, days int, vendor string) {
	relDate := catalog.DateReleased
	if len(relDate) > 10 {
		relDate = relDate[:10]
	}

	fmt.Printf("  %s%sカタログ%s : %s\n", colorBold, colorGreen, colorReset, catalog.Title)
	fmt.Printf("  バージョン: %-14s | リリース日: %s\n", catalog.CatalogVersion, relDate)
	fmt.Printf("  総CVE数  : %s%d件%s | 直近%d日間: %s%d件%s\n\n",
		colorBold, catalog.Count, colorReset,
		days,
		colorRed, len(recent), colorReset)

	if vendor != "" {
		fmt.Printf("  ベンダーフィルタ: %s\"%s\"%s\n\n", colorYellow, vendor, colorReset)
	}
}

// printVulnList は脆弱性の一覧を表示する
func printVulnList(vulns []Vulnerability, detail bool) {
	fmt.Printf("%s%s  %-20s %-22s %-18s %s%s\n",
		colorBold, colorCyan,
		"CVE ID", "ベンダー/プロジェクト", "製品", "追加日",
		colorReset)
	fmt.Println("  " + strings.Repeat("─", 76))

	for _, v := range vulns {
		t, _ := time.Parse("2006-01-02", v.DateAdded)
		daysSince := int(time.Since(t).Hours() / 24)

		// 経過日数に応じてカラーと優先度マークを変える
		var rowColor, priority string
		switch {
		case daysSince <= 3:
			rowColor = colorRed
			priority = "🔴"
		case daysSince <= 7:
			rowColor = colorYellow
			priority = "🟡"
		default:
			rowColor = colorReset
			priority = "  "
		}

		fmt.Printf("%s%s %-20s %-22s %-18s %s%s\n",
			rowColor,
			priority,
			trunc(v.CveID, 20),
			trunc(v.VendorProject, 22),
			trunc(v.Product, 18),
			v.DateAdded,
			colorReset)

		fmt.Printf("   %s%s%s\n", colorYellow, trunc(v.VulnerabilityName, 74), colorReset)

		if detail {
			if v.ShortDescription != "" {
				fmt.Printf("   %s説明%s: %s\n", colorDim, colorReset, trunc(v.ShortDescription, 72))
			}
			fmt.Printf("   %s対応%s: %s\n", colorDim, colorReset, trunc(v.RequiredAction, 72))
			fmt.Printf("   %s期限%s: %s\n", colorDim, colorReset, v.DueDate)
		}
		fmt.Println()
	}
}

// printVendorStats はベンダー別CVE件数のバーチャートを表示する
func printVendorStats(vulns []Vulnerability, days int) {
	vendorCount := make(map[string]int)
	for _, v := range vulns {
		vendorCount[v.VendorProject]++
	}

	var stats []vendorStat
	for name, count := range vendorCount {
		stats = append(stats, vendorStat{name, count})
	}
	sort.Slice(stats, func(i, j int) bool {
		if stats[i].count != stats[j].count {
			return stats[i].count > stats[j].count
		}
		return stats[i].name < stats[j].name
	})

	maxShow := 5
	if len(stats) < maxShow {
		maxShow = len(stats)
	}

	fmt.Printf("%s%s  ベンダー別CVE件数 TOP%d（直近%d日間）:%s\n",
		colorBold, colorCyan, maxShow, days, colorReset)

	for _, s := range stats[:maxShow] {
		barLen := s.count
		if barLen > 25 {
			barLen = 25
		}
		bar := strings.Repeat("█", barLen)
		overflow := ""
		if s.count > 25 {
			overflow = "+"
		}
		fmt.Printf("  %-22s %s%s%s%s (%d)\n",
			trunc(s.name, 22),
			colorRed, bar, overflow, colorReset,
			s.count)
	}
	fmt.Println()
}

// printFooter は終了メッセージを表示する
func printFooter(count, days int) {
	fmt.Printf("%s%s  ✅ スキャン完了 — 直近%d日間で %d件の悪用済みCVEを検出%s\n",
		colorBold, colorGreen, days, count, colorReset)
	fmt.Printf("  %sSource: %s%s\n\n", colorDim, kevURL, colorReset)
}

// fetchKEV はCISAのKEVカタログをHTTP GETで取得しデコードする
func fetchKEV() (*KEVCatalog, error) {
	client := &http.Client{Timeout: 30 * time.Second}
	req, err := http.NewRequest(http.MethodGet, kevURL, nil)
	if err != nil {
		return nil, fmt.Errorf("リクエスト生成失敗: %w", err)
	}
	req.Header.Set("User-Agent", "kev-watch/1.0 (security research tool)")
	req.Header.Set("Accept", "application/json")

	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("HTTP GET失敗: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("HTTPステータス %d", resp.StatusCode)
	}

	var catalog KEVCatalog
	if err := json.NewDecoder(resp.Body).Decode(&catalog); err != nil {
		return nil, fmt.Errorf("JSONデコード失敗: %w", err)
	}
	return &catalog, nil
}

// loadSampleData は内蔵サンプルデータをパースして返す
func loadSampleData() (*KEVCatalog, error) {
	var catalog KEVCatalog
	if err := json.Unmarshal([]byte(sampleJSON), &catalog); err != nil {
		return nil, fmt.Errorf("サンプルデータのパース失敗: %w", err)
	}
	return &catalog, nil
}

// filterVulns はカットオフ日時以降に追加されたCVEをベンダー名フィルタとともに抽出する
func filterVulns(vulns []Vulnerability, cutoff time.Time, vendor string) []Vulnerability {
	vendorLower := strings.ToLower(vendor)
	var result []Vulnerability
	for _, v := range vulns {
		t, err := time.Parse("2006-01-02", v.DateAdded)
		if err != nil {
			continue
		}
		if !t.After(cutoff) {
			continue
		}
		if vendor != "" && !strings.Contains(strings.ToLower(v.VendorProject), vendorLower) {
			continue
		}
		result = append(result, v)
	}
	return result
}

// trunc は文字列をmax文字に切り詰める（超過時は末尾に"..."を付加）
func trunc(s string, max int) string {
	runes := []rune(s)
	if len(runes) <= max {
		return s
	}
	return string(runes[:max-3]) + "..."
}
