#!/usr/bin/env python3
"""할 일 관리 (PyQt6).  pip install PyQt6  →  python todo_qt.py   /  데이터: ~/.todo_pyqt.json
변경: 제목 클릭 시에만 편집 사이드바 / 폴더 이모지 아이콘 / 태그 필터 / 검색(Ctrl+F) / 카드 뷰(Keep 스타일)
추가: 테이블 다중 선택(Shift+방향키·Shift/Ctrl+클릭·드래그) / Delete 삭제 / Ctrl+C·V 복사 / 드래그로 순서 변경 / F2 이름 변경
추가: 휴지통(삭제 → 휴지통, 원래 폴더·자리로 복구, 아이콘 변경) / 설정·데이터 파일 경로 변경 / 고정핀 이모지 변경 / 세부 메모 마크다운(편집·미리보기, 체크박스 클릭)
      지정한 경로는 ~/.donut_paths.json 에 기억됨 (기본값: 설정·데이터 모두 ~/.todo_pyqt.json)
추가: 열 너비 조절(머리글 경계선 드래그, 엑셀처럼) / 머리글 우클릭 = 열 너비 초기화 (작업 표·휴지통 표, 너비는 설정 파일에 저장)
추가: 행 높이 조절(표 왼쪽 가장자리의 행 경계선 드래그 = 개별, 여러 행 선택 후 끌면 함께 / 보기 메뉴 = 일괄) / 행 색상 지정(우클릭) + 색상별 정렬
      모든 열 필터(머리글의 깔때기 아이콘 클릭) / 우선순위·상태 레이블 직접 추가·편집(이름·색·중요도 순서·완료 여부·기본값)
추가: 모든 뷰 하단 가로 스크롤 / 테이블: 열 너비를 화면보다 넓게(엑셀식 개별 조절 + 오른쪽 여백)
      간트차트: 년 > 월 > 일 단위(Ctrl + 휠 위 = 세분화, Ctrl + 휠 아래 = 크게), ◀ ▶ 월 이동, 가로 스크롤·드래그로 끝없이 이전/다음 달 이동
      타임라인: 시작·종료·마감·완료 '사건'을 시간 순으로 보여주는 세로 이벤트 흐름(오늘 기준선, 월/날짜 묶음, 종류별 켜기/끄기)
추가: 설정 > 테마 드롭다운(기본 테마 + 내장 테마 23종) / 현재 색상을 사용자 테마로 저장·삭제 (설정 파일의 ui.usrthemes 에 저장)"""
import sys, os, json, re, uuid, time, calendar, math
from datetime import date, timedelta
from PyQt6.QtCore import Qt, QSize, QRect, QEvent, QTimer, QRectF, QPointF, QPropertyAnimation, QEasingCurve, QLocale, QItemSelectionModel, pyqtSignal, pyqtProperty, QObject, QByteArray, QMimeData, QModelIndex, QUrl, QPoint, QDate
from PyQt6.QtGui import (QColor, QPainter, QFont, QPen, QFontMetrics, QPixmap, QIcon, QShortcut, QKeySequence, QCursor, QPalette, QDesktopServices,
                         QTextDocument, QTextCursor, QTextBlockFormat, QTextFormat, QAbstractTextDocumentLayout, QPolygonF, QPainterPath)
from PyQt6.QtWidgets import *

FILE = os.path.expanduser("~/.todo_pyqt.json")      # 기본 설정/데이터 파일 (설정 창에서 경로 변경 가능)
PATHS = os.path.expanduser("~/.donut_paths.json")   # 사용자가 지정한 설정/데이터 파일 경로를 기억하는 파일
TRASH = "__trash__"                                 # 휴지통을 가리키는 특수 폴더 id
DEFPIN = "📌"                                       # 기본 고정핀 이모지
MIME = "application/x-donut-tasks"   # 작업 복사/붙여넣기용 클립보드 형식
CONFIRM_DELETE = True                 # Delete 키로 삭제할 때 확인 창을 띄울지 여부
LOGO = "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"  # 상단 제목 로고 (do.nut, PNG base64)
TR = {
"ko": dict(app="Do.Nut", add="+ 새 작업", done="완료함", selall="전체 선택", delsel="선택 삭제", settings="설정", tabs=["테이블", "간트차트", "캘린더", "타임라인", "카드"],
  cols=["작업명", "우선순위", "상태", "마감일", "타임라인", "태그"], P=["매우 높음", "높음", "보통", "낮음"], S=["착수 전", "진행 중", "대기", "완료"],
  memo="세부 메모", start="시작일", end="종료일", due="마감일", tags="태그 (쉼표 구분)", lang="언어", cn=["배경색", "패널색", "글자색", "강조색"],
  pcl="우선순위 색", scl="상태 색", font="글꼴", size="글자 크기", fsearch="글꼴 이름으로 검색", fall="전체 글꼴 목록", apply="적용", exp="내보내기", imp="불러오기", reset="테마 초기화",
  ask="선택한 완료 항목을 휴지통으로 옮길까요?", none="—", clear="날짜 지우기", del1="이 작업 삭제", empty="날짜가 있는 작업이 없습니다", ph="작업명 입력", detail="세부 내용",
  folders="폴더", allf="전체", newf="새 폴더", rn="이름 바꾸기", delf="폴더 삭제", folder="폴더", askf="이 폴더를 삭제할까요?\n폴더 안의 작업은 삭제되지 않고 '전체'로 이동합니다.",
  fset="설정", ftask="작업 데이터", err="오류", badset="올바른 설정 파일이 아닙니다.", badtask="올바른 작업 데이터 파일이 아닙니다.", merge="합치기", replace="덮어쓰기", impok="{n}개의 작업을 불러왔습니다.", ftog="폴더 목록 접기/펼치기",
  impq="현재 작업 데이터에 어떻게 불러올까요?\n\n합치기: 같은 작업은 파일 내용으로 갱신하고, 나머지는 그대로 둡니다.\n덮어쓰기: 현재 작업과 폴더를 모두 파일 내용으로 바꿉니다.",
  search="검색 (Ctrl+F)", tagf="태그", tagall="필터 해제", tagand="선택한 태그를 모두 포함 (AND)", notag="태그가 없습니다", icon="아이콘 변경", deficon="기본 아이콘으로", emo="이모지 직접 입력 (Win + . 으로 이모지 창)", empty2="표시할 작업이 없습니다", askdel="선택한 작업 {n}개를 휴지통으로 옮길까요?",
  trash="휴지통", restore="복구", purge="영구 삭제", emptyt="휴지통 비우기", tempty="휴지통이 비어 있습니다", ofolder="원래 폴더", dtime="삭제한 날짜", nsel="{n}개",
  askpurge="선택한 작업 {n}개를 영구 삭제할까요?\n되돌릴 수 없습니다.", askempty="휴지통의 작업 {n}개를 모두 영구 삭제할까요?\n되돌릴 수 없습니다.",
  pinemo="고정핀 이모지", ppath="설정 파일 경로", dpath="데이터 파일 경로", chg="변경…", deflt="기본값", opendir="폴더 열기", badpath="이 위치에 파일을 저장할 수 없습니다.",
  pathq="선택한 위치에 이미 파일이 있습니다.\n\n불러오기: 그 파일의 내용을 불러와 사용합니다.\n덮어쓰기: 현재 내용을 그 파일에 저장합니다.",
  medit="편집", mprev="미리보기", mdhint="세부 메모 (마크다운 지원 · Ctrl+E 미리보기)", mdempty="메모 없음 · 클릭하여 작성"),
"en": dict(app="Do.Nut", add="+ New task", done="Done box", selall="Select all", delsel="Delete selected", settings="Settings", tabs=["Table", "Gantt", "Calendar", "Timeline", "Cards"],
  cols=["Task", "Priority", "Status", "Due", "Timeline", "Tags"], P=["Very high", "High", "Normal", "Low"], S=["Not started", "In progress", "On hold", "Done"],
  memo="Notes", start="Start", end="End", due="Due", tags="Tags (comma separated)", lang="Language", cn=["Background", "Panel", "Text", "Accent"],
  pcl="Priority color", scl="Status color", font="Font", size="Font size", fsearch="Search fonts by name", fall="All fonts", apply="Apply", exp="Export", imp="Import", reset="Reset theme",
  ask="Move the selected done tasks to the trash?", none="—", clear="Clear date", del1="Delete task", empty="No tasks with dates", ph="Task name", detail="Details",
  folders="Folders", allf="All", newf="New folder", rn="Rename", delf="Delete folder", folder="Folder", askf="Delete this folder?\nTasks inside are kept and moved to 'All'.",
  fset="Settings", ftask="Task data", err="Error", badset="Not a valid settings file.", badtask="Not a valid task data file.", merge="Merge", replace="Replace", impok="Imported {n} task(s).", ftog="Collapse/expand folders",
  impq="How do you want to import into the current task data?\n\nMerge: tasks with the same ID are updated from the file; everything else is kept.\nReplace: current tasks and folders are replaced by the file.",
  search="Search (Ctrl+F)", tagf="Tags", tagall="Clear filter", tagand="Match all selected tags (AND)", notag="No tags", icon="Change icon", deficon="Use default icon", emo="Type an emoji", empty2="No tasks to show", askdel="Move {n} selected task(s) to the trash?",
  trash="Trash", restore="Restore", purge="Delete forever", emptyt="Empty trash", tempty="Trash is empty", ofolder="Original folder", dtime="Deleted", nsel="{n}",
  askpurge="Permanently delete {n} selected task(s)?\nThis cannot be undone.", askempty="Permanently delete all {n} task(s) in the trash?\nThis cannot be undone.",
  pinemo="Pin emoji", ppath="Settings file", dpath="Data file", chg="Change…", deflt="Default", opendir="Open folder", badpath="Cannot save a file at this location.",
  pathq="A file already exists at the selected location.\n\nImport: load and use the contents of that file.\nReplace: save the current contents to that file.",
  medit="Edit", mprev="Preview", mdhint="Notes (Markdown supported · Ctrl+E to preview)", mdempty="No notes · click to write"),
"ja": dict(app="Do.Nut", add="+ 新規タスク", done="完了ボックス", selall="全選択", delsel="選択削除", settings="設定", tabs=["テーブル", "ガント", "カレンダー", "タイムライン", "カード"],
  cols=["タスク名", "優先度", "状態", "期限", "タイムライン", "タグ"], P=["非常に高い", "高い", "普通", "低い"], S=["未着手", "進行中", "待機", "完了"],
  memo="詳細メモ", start="開始日", end="終了日", due="期限", tags="タグ (カンマ区切り)", lang="言語", cn=["背景色", "パネル色", "文字色", "強調色"],
  pcl="優先度の色", scl="状態の色", font="フォント", size="文字サイズ", fsearch="フォント名で検索", fall="すべてのフォント", apply="適用", exp="エクスポート", imp="インポート", reset="テーマ初期化",
  ask="選択した完了タスクをゴミ箱に移動しますか?", none="—", clear="日付を消す", del1="タスクを削除", empty="日付付きのタスクがありません", ph="タスク名を入力", detail="詳細",
  folders="フォルダ", allf="すべて", newf="新しいフォルダ", rn="名前を変更", delf="フォルダを削除", folder="フォルダ", askf="このフォルダを削除しますか?\n中のタスクは削除されず「すべて」に移動します。",
  fset="設定", ftask="タスクデータ", err="エラー", badset="有効な設定ファイルではありません。", badtask="有効なタスクデータファイルではありません。", merge="統合", replace="上書き", impok="{n}件のタスクを読み込みました。", ftog="フォルダの折りたたみ/展開",
  impq="現在のタスクデータにどう読み込みますか?\n\n統合: 同じタスクはファイルの内容で更新し、他はそのまま残します。\n上書き: 現在のタスクとフォルダをすべてファイルの内容に置き換えます。",
  search="検索 (Ctrl+F)", tagf="タグ", tagall="フィルター解除", tagand="選択したタグをすべて含む (AND)", notag="タグがありません", icon="アイコンを変更", deficon="デフォルトのアイコン", emo="絵文字を入力", empty2="表示するタスクがありません", askdel="選択した{n}件のタスクをゴミ箱に移動しますか?",
  trash="ゴミ箱", restore="復元", purge="完全に削除", emptyt="ゴミ箱を空にする", tempty="ゴミ箱は空です", ofolder="元のフォルダ", dtime="削除日時", nsel="{n}件",
  askpurge="選択した{n}件のタスクを完全に削除しますか?\n元に戻せません。", askempty="ゴミ箱の{n}件のタスクをすべて完全に削除しますか?\n元に戻せません。",
  pinemo="ピンの絵文字", ppath="設定ファイルのパス", dpath="データファイルのパス", chg="変更…", deflt="デフォルト", opendir="フォルダを開く", badpath="この場所にファイルを保存できません。",
  pathq="選択した場所にすでにファイルがあります。\n\nインポート: そのファイルの内容を読み込んで使用します。\n上書き: 現在の内容をそのファイルに保存します。",
  medit="編集", mprev="プレビュー", mdhint="詳細メモ (Markdown対応 · Ctrl+E でプレビュー)", mdempty="メモなし · クリックして入力"),
}
for _k, _v in {"ko": dict(colw1="이 열 너비 초기화", colwall="모든 열 너비 초기화"),
               "en": dict(colw1="Reset this column width", colwall="Reset all column widths"),
               "ja": dict(colw1="この列の幅をリセット", colwall="すべての列の幅をリセット")}.items():
    TR[_k].update(_v)
for _k, _v in {
    "ko": dict(theme="테마", th_def="기본 테마", th_cus="사용자 지정 (수정됨)", th_save="테마 저장…", th_del="삭제", th_name="저장할 테마 이름", th_user="사용자 테마",
               th_over="'{n}' 테마가 이미 있습니다.\n현재 색상으로 덮어쓸까요?", th_resv="기본 제공 테마의 이름은 사용할 수 없습니다.", th_delq="사용자 테마 '{n}'을(를) 삭제할까요?"),
    "en": dict(theme="Theme", th_def="Default theme", th_cus="Custom (modified)", th_save="Save theme…", th_del="Delete", th_name="Theme name", th_user="My themes",
               th_over="A theme named '{n}' already exists.\nOverwrite it with the current colors?", th_resv="You can't use the name of a built-in theme.", th_delq="Delete the custom theme '{n}'?"),
    "ja": dict(theme="テーマ", th_def="デフォルトテーマ", th_cus="カスタム (変更あり)", th_save="テーマを保存…", th_del="削除", th_name="テーマ名", th_user="マイテーマ",
               th_over="「{n}」というテーマはすでにあります。\n現在の色で上書きしますか?", th_resv="組み込みテーマの名前は使えません。", th_delq="カスタムテーマ「{n}」を削除しますか?")}.items():
    TR[_k].update(_v)
# 간트차트 단위 / 타임라인
TR["ko"].update(g_year="년", g_month="월", g_day="일", g_today="오늘", g_pm="이전 달", g_nm="다음 달", g_py="이전 해", g_ny="다음 해",
    g_hint="Ctrl + 휠 = 단위 변경", g_tip="Ctrl + 휠 위 = 더 세분화 (년 → 월 → 일)\nCtrl + 휠 아래 = 더 크게 (일 → 월 → 년)\n휠 = 세로 스크롤 · Shift + 휠 / 가로 스크롤 / 빈 곳 드래그 = 기간 이동",
    tl_start="시작", tl_end="종료", tl_due="마감", tl_done="완료", tl_goto="오늘로", tl_none="오늘 일정 없음", tl_over="기한 지남",
    tl_sum="기한 지남 {o} · 오늘 {t} · 7일 이내 {k}", tl_empty="표시할 사건이 없습니다 (시작·종료·마감일이나 완료 기록이 있는 작업이 나타납니다)",
    rel0="오늘", relp1="내일", relm1="어제", relf="{n}일 후", relb="{n}일 전", ndays="{n}일")
TR["en"].update(g_year="Year", g_month="Month", g_day="Day", g_today="Today", g_pm="Previous month", g_nm="Next month", g_py="Previous year", g_ny="Next year",
    g_hint="Ctrl + wheel = change unit", g_tip="Ctrl + wheel up = finer (Year → Month → Day)\nCtrl + wheel down = coarser (Day → Month → Year)\nWheel = vertical scroll · Shift + wheel / horizontal scroll / drag empty area = move in time",
    tl_start="Start", tl_end="End", tl_due="Due", tl_done="Done", tl_goto="Go to today", tl_none="Nothing today", tl_over="Overdue",
    tl_sum="Overdue {o} · Today {t} · Next 7 days {k}", tl_empty="No events to show (tasks with start/end/due dates or completion records appear here)",
    rel0="Today", relp1="Tomorrow", relm1="Yesterday", relf="in {n} days", relb="{n} days ago", ndays="{n} days")
TR["ja"].update(g_year="年", g_month="月", g_day="日", g_today="今日", g_pm="前の月", g_nm="次の月", g_py="前の年", g_ny="次の年",
    g_hint="Ctrl + ホイール = 単位変更", g_tip="Ctrl + ホイール上 = 細かく (年 → 月 → 日)\nCtrl + ホイール下 = 大きく (日 → 月 → 年)\nホイール = 縦スクロール · Shift + ホイール / 横スクロール / 空き領域ドラッグ = 期間移動",
    tl_start="開始", tl_end="終了", tl_due="期限", tl_done="完了", tl_goto="今日へ", tl_none="今日の予定なし", tl_over="期限切れ",
    tl_sum="期限切れ {o} · 今日 {t} · 7日以内 {k}", tl_empty="表示する出来事がありません (開始・終了・期限日または完了記録のあるタスクが表示されます)",
    rel0="今日", relp1="明日", relm1="昨日", relf="{n}日後", relb="{n}日前", ndays="{n}日")
# 행 높이 / 행 색상 / 열 필터 / 레이블 편집
TR["ko"].update(view="보기", rowhall="모든 행 높이…", rowhsel="선택한 행 높이…", rowhrst="선택한 행 높이 기본값으로", rowhclr="개별 행 높이 모두 초기화",
    rowhq="행 높이 (px)", rowhall2="개별로 지정한 행 높이도 모두 이 값으로 바꾸기", rowhtip="경계선을 끌어 행 높이 조절\n여러 행을 선택한 뒤 끌면 함께 바뀜 · 경계선 더블클릭 = 기본 높이",
    rcol="행 색상", rcnone="색 없음", rcpick="직접 선택…", csort="색상별 정렬", manual="수동 순서 (정렬 해제)", sasc="오름차순 정렬", sdesc="내림차순 정렬", sclr="정렬 해제",
    fclr="이 열 필터 해제", fall0="모든 필터 해제", fltn="필터 {n}", fltdo="필터…", ftext="작업명에 포함된 글자 (띄어쓰기 = 모두 포함)", fpinh="고정핀", fpin="고정됨", fnopin="고정 안 됨",
    fcol="색상", fnotag="(태그 없음)", dc=["날짜 없음", "기한 지남", "오늘", "7일 이내", "그 이후"], tc=["기간 없음", "진행 기간 (오늘 포함)", "지난 기간", "예정된 기간"],
    labels="레이블", lbp="우선순위 레이블", lbs="상태 레이블", lbedit="레이블 편집…", lbadd="레이블 추가", lbnew="새 레이블", lbdone="완료로 취급", lbdef="새 작업 기본값",
    lbhp="위에 있을수록 중요도가 높습니다. ▲▼로 순서를 바꾸면 정렬·필터 목록이 이 순서를 따릅니다.",
    lbhs="위에 있을수록 정렬 시 앞에 옵니다. '완료로 취급'을 켠 상태의 작업은 완료함으로 이동합니다.",
    lbdel="삭제한 레이블을 쓰던 작업 {n}개는 '{name}'(으)로 바뀝니다.\n계속할까요?", cancel="취소")
TR["en"].update(view="View", rowhall="All row heights…", rowhsel="Height of selected rows…", rowhrst="Reset selected row heights", rowhclr="Reset all individual row heights",
    rowhq="Row height (px)", rowhall2="Also apply to rows with an individual height", rowhtip="Drag a boundary to resize the row\nSelect several rows and drag to resize them together · double-click = default",
    rcol="Row color", rcnone="No color", rcpick="Custom…", csort="Sort by color", manual="Manual order (no sort)", sasc="Sort ascending", sdesc="Sort descending", sclr="Clear sorting",
    fclr="Clear this column filter", fall0="Clear all filters", fltn="{n} filter(s)", fltdo="Filter…", ftext="Text in task name (space = all words)", fpinh="Pin", fpin="Pinned", fnopin="Not pinned",
    fcol="Color", fnotag="(No tags)", dc=["No date", "Overdue", "Today", "Within 7 days", "Later"], tc=["No period", "Ongoing (includes today)", "Past", "Upcoming"],
    labels="Labels", lbp="Priority labels", lbs="Status labels", lbedit="Edit labels…", lbadd="Add label", lbnew="New label", lbdone="Counts as done", lbdef="Default for new tasks",
    lbhp="Higher in the list = more important. Reorder with ▲▼; sorting and filter lists follow this order.",
    lbhs="Higher in the list comes first when sorting. Tasks with a 'counts as done' status move to the Done box.",
    lbdel="{n} task(s) using deleted labels will be changed to '{name}'.\nContinue?", cancel="Cancel")
TR["ja"].update(view="表示", rowhall="すべての行の高さ…", rowhsel="選択した行の高さ…", rowhrst="選択した行の高さを既定に戻す", rowhclr="個別の行の高さをすべてリセット",
    rowhq="行の高さ (px)", rowhall2="個別に指定した行の高さもすべてこの値にする", rowhtip="境界線をドラッグして行の高さを調整\n複数行を選択してドラッグすると一括変更 · ダブルクリック = 既定",
    rcol="行の色", rcnone="色なし", rcpick="色を選択…", csort="色で並べ替え", manual="手動順 (並べ替え解除)", sasc="昇順で並べ替え", sdesc="降順で並べ替え", sclr="並べ替えを解除",
    fclr="この列のフィルターを解除", fall0="すべてのフィルターを解除", fltn="フィルター {n}", fltdo="フィルター…", ftext="タスク名に含む文字 (空白 = すべて含む)", fpinh="ピン", fpin="ピン留め", fnopin="ピンなし",
    fcol="色", fnotag="(タグなし)", dc=["日付なし", "期限切れ", "今日", "7日以内", "それ以降"], tc=["期間なし", "進行中 (今日を含む)", "過去の期間", "予定の期間"],
    labels="ラベル", lbp="優先度ラベル", lbs="状態ラベル", lbedit="ラベルを編集…", lbadd="ラベルを追加", lbnew="新しいラベル", lbdone="完了として扱う", lbdef="新規タスクの既定値",
    lbhp="上にあるほど重要度が高くなります。▲▼で順序を変えると並べ替え・フィルターもこの順になります。",
    lbhs="上にあるほど並べ替えで先に来ます。「完了として扱う」状態のタスクは完了ボックスへ移動します。",
    lbdel="削除したラベルを使っていた{n}件のタスクは「{name}」に変更されます。\n続けますか?", cancel="キャンセル")
DT = dict(bg="#14161b", panel="#1c1f27", fg="#e8eaf0", accent="#7c9cff", font="Segoe UI", size=10, pin=DEFPIN,
          pc=["#ef4444", "#f59e0b", "#3b82f6", "#6b7280"], sc=["#6b7280", "#3b82f6", "#f59e0b", "#22c55e"])
TKEYS = ("bg", "panel", "fg", "accent")   # 테마가 바꾸는 색 4개 (글꼴·글자 크기·고정핀은 그대로 유지)
# 내장 테마: 이름 → (배경, 패널, 글자, 강조).  '기본 테마'는 위 DT 의 색.  순서 = 드롭다운 순서
BT = {n: dict(zip(TKEYS, c)) for n, c in [
    ("light",                  ("#ffffff", "#f3f4f6", "#1f2937", "#3b82f6")),
    ("dark gray",              ("#1e1e1e", "#2a2a2a", "#e0e0e0", "#8ab4f8")),
    ("Latte",                  ("#eff1f5", "#e6e9ef", "#4c4f69", "#1e66f5")),
    ("Tokyo Night",            ("#1a1b26", "#24283b", "#c0caf5", "#7aa2f7")),
    ("Frappé",                 ("#303446", "#292c3c", "#c6d0f5", "#8caaee")),
    ("Macchiato",              ("#24273a", "#1e2030", "#cad3f5", "#8aadf4")),
    ("pastel mint",            ("#f0faf5", "#dff3e8", "#2f4f43", "#4fb99a")),
    ("pastel pink",            ("#fff5f8", "#fde4ec", "#5a3a46", "#f08db0")),
    ("retro",                  ("#f2e8cf", "#e6d8b5", "#3d2c1e", "#d9593d")),
    ("cyberpunk",              ("#0d0221", "#1a0b38", "#d1f7ff", "#ff2a6d")),
    ("classic windows",        ("#c0c0c0", "#dfdfdf", "#000000", "#000080")),
    ("Sage green",             ("#eef2ea", "#dfe7d8", "#3a4a3a", "#6b8f71")),
    ("Dark academia",          ("#2a2118", "#362b20", "#e6d8c3", "#b08d57")),
    ("Japanese Cherry Blossom", ("#231a1f", "#2f2328", "#f6e6ea", "#f4a7b9")),
    ("Nordic Forest",          ("#1f2a24", "#27352d", "#dde7df", "#7fb685")),
    ("Mountain Lake",          ("#eaf2f4", "#d6e6ea", "#23404a", "#3f8fa8")),
    ("Ocean",                  ("#082032", "#0e2f47", "#d6ecf7", "#2ec4b6")),
    ("Blue sky",               ("#eaf6ff", "#d4ebfb", "#1f3a52", "#3aa0f0")),
    ("Deep blue",              ("#0a1128", "#121c3f", "#dce4ff", "#4f7cff")),
    ("discord",                ("#313338", "#2b2d31", "#dbdee1", "#5865f2")),
    ("Pokémon",                ("#fff9e5", "#fbeab5", "#2a2a3a", "#ee1515")),
    ("ark",                    ("#12181b", "#1b2529", "#cfe3e6", "#f0a030")),
    ("Atom one dark",          ("#282c34", "#21252b", "#abb2bf", "#61afef")),
    ("black mint",             ("#000000", "#0c1512", "#d5f5e8", "#3ef0b0")),
]}
PAL = ["#ef4444", "#f97316", "#f59e0b", "#eab308", "#84cc16", "#22c55e", "#14b8a6", "#06b6d4", "#3b82f6", "#6366f1", "#a855f7", "#ec4899", "#6b7280"]   # 행 색상 팔레트 (색상별 정렬도 이 순서)
ROWTINT = .30          # 행 색상 진하기 (0~1, 클수록 진함)
DEFROWH = 46           # 기본 행 높이
BUILTIN = {"prio": ["p0", "p1", "p2", "p3"], "status": ["s0", "s1", "s2", "s3"]}   # 기본 레이블 id (이름을 바꾸지 않으면 언어에 맞춰 표시)


def nat(x): return [int(p) if p.isdigit() else p.lower() for p in re.split(r"(\d+)", str(x))]
def mix(a, b, k): a, b = QColor(a), QColor(b); return QColor(*[int(a.getRgb()[i] * k + b.getRgb()[i] * (1 - k)) for i in range(3)]).name()
def ontext(c): q = QColor(c); return "#000" if (q.red() * 299 + q.green() * 587 + q.blue() * 114) / 1000 > 140 else "#fff"

QSS = """
*{font-family:"@font";font-size:@sizept;color:@fg;outline:0}
QMainWindow,QDialog,QStackedWidget,QScrollArea{background:@bg;border:0}
#side{background:@pn;border-left:1px solid @bd}#title{font-size:16pt;font-weight:700}#nm{font-size:13pt;font-weight:700}#hr{background:@dv;border:0}
QTableWidget{background:@bg;border:1px solid @bd;border-radius:12px;selection-background-color:transparent}
QTableWidget::item{padding-left:8px;border-bottom:1px solid @bd}QTableWidget::item:selected{background:@hv;color:@fg}
QHeaderView::section{background:@bg;color:@mu;border:0;border-bottom:1px solid @bd;padding:8px;font-weight:600}
QLineEdit,QTextEdit{background:@bg;border:1px solid @bd;border-radius:8px;padding:6px 8px;selection-background-color:@ac;selection-color:@on}
QLineEdit:focus,QTextEdit:focus{border-color:@ac}
QPushButton{background:@pn;border:1px solid @bd;border-radius:8px;padding:7px 14px}QPushButton:hover{border-color:@ac}
QPushButton#primary{background:@ac;color:@on;border:0;font-weight:600}
QPushButton#seg{border:0;background:transparent;border-radius:8px}QPushButton#seg:checked{background:@ac;color:@on;font-weight:600}
QPushButton#cell{background:transparent;border:0;text-align:left;padding:4px 8px;border-radius:6px}QPushButton#cell:hover{background:@pn}
QPushButton#danger{color:#ef4444}
QPushButton:disabled{color:@mu}QPushButton#primary:disabled{background:@bd;color:@mu}
QTextBrowser#mdv{padding:6px 10px}
QToolButton#pin{border:0;padding:0;border-radius:6px;background:transparent}QToolButton#pin:hover{background:@hv}
QPushButton#ico{background:transparent;border:0;border-radius:8px;padding:0;font-size:14pt}QPushButton#ico:hover{background:@pn}
QListWidget#folders{background:transparent;border:0}QListWidget#folders::item{padding:7px 8px;border-radius:8px;margin:1px 0}QListWidget#folders::item:hover{background:@pn}QListWidget#folders::item:selected{background:@hv;color:@fg}QLabel#mu{color:@mu;font-weight:600}
QMenu{background:@pn;border:1px solid @bd;border-radius:8px;padding:4px}QMenu::item{padding:6px 20px;border-radius:6px}QMenu::item:selected{background:@ac;color:@on}
QComboBox{background:@bg;border:1px solid @bd;border-radius:8px;padding:5px 8px}QComboBox::drop-down{width:0;border:0}
QComboBox QAbstractItemView{background:@pn;border:1px solid @bd;selection-background-color:@ac;selection-color:@on}
QListView#fontpop{background:@pn;border:1px solid @bd;selection-background-color:@ac;selection-color:@on}
QScrollBar:vertical{width:12px;background:@pn;border:0;margin:0}QScrollBar:horizontal{height:12px;background:@pn;border:0;margin:0}
QScrollBar::handle{background:@dv;border-radius:5px;min-height:30px;min-width:30px;margin:2px}QScrollBar::handle:hover{background:@mu}QScrollBar::handle:pressed{background:@ac}
QScrollBar::add-line,QScrollBar::sub-line{width:0;height:0;border:0;background:transparent}QScrollBar::add-page,QScrollBar::sub-page{background:transparent}
QAbstractScrollArea::corner{background:@pn;border:0}
QCalendarWidget QWidget{background:@pn}QCalendarWidget QAbstractItemView:enabled{selection-background-color:@ac;selection-color:@on;color:@fg}
QCheckBox::indicator{width:16px;height:16px;border-radius:4px;border:1px solid @mu}QCheckBox::indicator:checked{background:@ac;border-color:@ac}
QPushButton#flt::menu-indicator{image:none;width:0}QPushButton#flt[on="true"]{border-color:@ac;color:@ac;font-weight:600}
QHeaderView#fh::section{padding-right:34px}
QHeaderView#rowgrip::section{padding:0;border:0;border-bottom:1px solid @bd;background:@bg}QHeaderView#rowgrip::section:hover{background:@hv}
QTableCornerButton::section{background:@bg;border:0}
"""
def qss(t):
    m = {"@font": t["font"], "@size": str(t["size"]), "@bg": t["bg"], "@pn": t["panel"], "@fg": t["fg"], "@ac": t["accent"], "@bd": mix(t["fg"], t["bg"], .14),
         "@mu": mix(t["fg"], t["bg"], .55), "@dv": mix(t["fg"], t["bg"], .3), "@hv": mix(t["accent"], t["bg"], .2), "@on": ontext(t["accent"])}
    s = QSS
    for k, v in m.items(): s = s.replace(k, v)
    return s
def ficon(c):
    pm = QPixmap(18, 18); pm.fill(Qt.GlobalColor.transparent); p = QPainter(pm); p.setRenderHint(QPainter.RenderHint.Antialiasing); p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor(c))
    p.drawRoundedRect(QRectF(1, 3, 7, 5), 1.5, 1.5); p.drawRoundedRect(QRectF(1, 5, 16, 11), 2.5, 2.5); p.end(); return QIcon(pm)
def sw(c, n=14):
    """색 견본 아이콘 (행 색상·레이블 색 메뉴용)"""
    pm = QPixmap(n, n); pm.fill(Qt.GlobalColor.transparent); p = QPainter(pm); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QPen(QColor(0, 0, 0, 60), 1)); p.setBrush(QColor(c)); p.drawRoundedRect(QRectF(.5, .5, n - 1, n - 1), 3, 3); p.end(); return QIcon(pm)
def ticon(c):
    """기본 휴지통 아이콘 (폴더 아이콘과 같은 크기/색 규칙)"""
    pm = QPixmap(18, 18); pm.fill(Qt.GlobalColor.transparent); p = QPainter(pm); p.setRenderHint(QPainter.RenderHint.Antialiasing); p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor(c))
    p.drawRoundedRect(QRectF(6.5, 1, 5, 2.6), 1, 1); p.drawRoundedRect(QRectF(2, 3.4, 14, 2.4), 1.2, 1.2); p.drawRoundedRect(QRectF(3.5, 6.8, 11, 10.2), 2, 2)
    p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear); p.drawRect(QRectF(6.4, 9, 1.4, 5.8)); p.drawRect(QRectF(10.2, 9, 1.4, 5.8)); p.end(); return QIcon(pm)
def eicon(e, n=18):
    """이모지 문자를 폴더 아이콘으로 렌더링"""
    k = 3; pm = QPixmap(n * k, n * k); pm.fill(Qt.GlobalColor.transparent); p = QPainter(pm); p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    f = QFont(); f.setPixelSize(int(n * k * .74)); p.setFont(f); p.setPen(QColor("#888"))
    p.drawText(QRectF(0, 0, n * k, n * k), Qt.AlignmentFlag.AlignCenter, e); p.end(); return QIcon(pm)
EMO = "📁 📂 🗂️ 📌 ⭐ ❤️ 🔥 ✅ 📝 📚 💼 🏠 🛒 💡 🎯 🚀 🎨 🎵 🎮 ✈️ 🏃 💪 🍽️ ☕ 💰 📅 🔧 💻 📱 🌱 🐶 🎁 🏥 🎓 ⚽ 🌙 🧪 📦 🔒 🎉 🗑️ ♻️ 🧹 📍".split()
def clean_theme(t):
    """불러온 설정 검증: 유효한 값만 남김 (없으면 None)"""
    if not isinstance(t, dict): return None
    o = {}; ok = lambda c: isinstance(c, str) and QColor(c).isValid()
    for k in ("bg", "panel", "fg", "accent"):
        if ok(t.get(k)): o[k] = QColor(t[k]).name()
    for k in ("pc", "sc"):
        v = t.get(k)
        if isinstance(v, list) and len(v) == 4 and all(ok(c) for c in v): o[k] = [QColor(c).name() for c in v]
    if isinstance(t.get("font"), str) and t["font"].strip(): o["font"] = t["font"]
    if isinstance(t.get("size"), int) and not isinstance(t["size"], bool) and 8 <= t["size"] <= 24: o["size"] = t["size"]
    if isinstance(t.get("pin"), str) and 0 < len(t["pin"].strip()) <= 8: o["pin"] = t["pin"].strip()
    return o or None
def clean_ut(raw):
    """사용자 테마 모음 검증: {이름: {bg, panel, fg, accent}} (색 4개가 모두 유효한 것만)"""
    o = {}
    for n, v in (raw.items() if isinstance(raw, dict) else []):
        c = clean_theme(v)
        if isinstance(n, str) and n.strip() and c and all(k in c for k in TKEYS): o[n.strip()[:30]] = {k: c[k] for k in TKEYS}
    return o
def tsw(c, n=16):
    """테마 견본 아이콘: 배경색 칸 + 패널 띠 + 강조색 점 (c = (bg, panel, fg, accent))"""
    pm = QPixmap(n, n); pm.fill(Qt.GlobalColor.transparent); p = QPainter(pm); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QPen(QColor(128, 128, 128, 150), 1)); p.setBrush(QColor(c[0])); p.drawRoundedRect(QRectF(.5, .5, n - 1, n - 1), 3, 3)
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor(c[1])); p.drawRoundedRect(QRectF(2, n * .62, n - 4, n * .26), 1.5, 1.5)
    p.setBrush(QColor(c[3])); p.drawEllipse(QRectF(n * .3, n * .17, n * .4, n * .4)); p.end(); return QIcon(pm)
def norm_task(t, used):
    """불러온 작업 1건을 앱이 기대하는 형태로 정규화 (누락/잘못된 값 보정)"""
    if not isinstance(t, dict): return None
    def lv(v, pre):
        """레이블 id. 예전 형식(0~3 숫자)은 기본 레이블 id(p0~p3 / s0~s3)로 바꿈. 존재 여부는 Win.lab_fix에서 확인"""
        if isinstance(v, bool): return ""
        if isinstance(v, int) or (isinstance(v, str) and v.strip().isdigit()):
            n = int(v); return f"{pre}{n}" if 0 <= n <= 3 else ""
        return v.strip()[:40] if isinstance(v, str) else ""
    def dt(v):
        try: return date.fromisoformat(str(v)).isoformat() if v else ""
        except Exception: return ""
    i = str(t.get("id") or "").strip()
    while not i or i in used: i = uuid.uuid4().hex[:8]
    used.add(i); tg = t.get("tags", [])
    if isinstance(tg, str): tg = tg.split(",")
    tg = [str(a).strip() for a in tg if str(a).strip()] if isinstance(tg, list) else []
    try: da = float(t.get("done_at") or 0)
    except Exception: da = 0
    c = t.get("color"); c = QColor(c).name() if isinstance(c, str) and c.strip() and QColor(c).isValid() else ""
    try: rh = int(t.get("rowh") or 0)
    except Exception: rh = 0
    rh = rh if 22 <= rh <= 300 else 0
    return dict(id=i, name=str(t.get("name") or ""), prio=lv(t.get("prio"), "p"), status=lv(t.get("status"), "s"), due=dt(t.get("due")), start=dt(t.get("start")), end=dt(t.get("end")),
                tags=tg, memo=str(t.get("memo") or ""), pin=bool(t.get("pin")), done_at=da, folder=str(t.get("folder") or ""), color=c, rowh=rh)
def norm_trash(t, used):
    """휴지통 항목 1건 정규화: 작업 필드 + 삭제 시각(deleted_at) + 삭제 전 위치(pos: 목록 순번, after: 바로 앞 작업 id)"""
    x = norm_task(t, used)
    if not x: return None
    try: x["deleted_at"] = float(t.get("deleted_at") or 0) or time.time()
    except Exception: x["deleted_at"] = time.time()
    try: x["pos"] = max(int(t.get("pos") or 0), 0)
    except Exception: x["pos"] = 0
    x["after"] = str(t.get("after") or ""); return x
def norm_folders(raw, newname="—"):
    seen = set(); out = []
    for f in (raw if isinstance(raw, list) else []):
        if isinstance(f, dict) and str(f.get("id") or "").strip() and str(f["id"]) not in seen and str(f["id"]) != TRASH:
            seen.add(str(f["id"])); out.append(dict(id=str(f["id"]), name=str(f.get("name") or "").strip() or newname, icon=str(f.get("icon") or "")[:8]))
    return out
def norm_labels(raw, theme=None):
    """우선순위/상태 레이블 정규화. {kind: {items: [{id, name, color, (done)}], default: id}}
    - items 순서 = 중요도 순서 (위가 높음)  - name이 비어 있는 기본 레이블은 언어별 기본 이름으로 표시
    - 레이블이 없으면(예전 데이터) 기본 4개를 만들고, 색은 예전 테마의 우선순위/상태 색을 그대로 사용"""
    theme = theme if isinstance(theme, dict) else DT; out = {}
    for k in ("prio", "status"):
        r = raw.get(k) if isinstance(raw, dict) else None; items = []; seen = set()
        if isinstance(r, dict) and isinstance(r.get("items"), list):
            for l in r["items"]:
                if not isinstance(l, dict): continue
                i = str(l.get("id") or "").strip()[:40]
                if not i or i in seen: continue
                c = l.get("color"); c = QColor(c).name() if isinstance(c, str) and QColor(c).isValid() else "#6b7280"
                o = dict(id=i, name=str(l.get("name") or "").strip()[:40], color=c)
                if k == "status": o["done"] = bool(l.get("done"))
                seen.add(i); items.append(o)
        if not items:
            cols = theme.get("pc" if k == "prio" else "sc")
            cols = cols if isinstance(cols, list) and len(cols) == 4 else DT["pc" if k == "prio" else "sc"]
            for n, b in enumerate(BUILTIN[k]):
                o = dict(id=b, name="", color=cols[n])
                if k == "status": o["done"] = n == 3
                items.append(o)
        ids = [l["id"] for l in items]; d = r.get("default") if isinstance(r, dict) else None
        if d not in ids: d = ("p2" if k == "prio" else "s0") if ("p2" if k == "prio" else "s0") in ids else ids[0]
        out[k] = dict(items=items, default=d)
    return out
# ----- 파일 입출력 (설정 파일 / 데이터 파일 경로 분리)
def read_json(p):
    try:
        with open(p, encoding="utf-8") as fh: j = json.load(fh)
        return j if isinstance(j, dict) else None
    except Exception:
        return None
def write_json(p, obj):
    """임시 파일에 먼저 쓴 뒤 교체 (저장 도중 꺼져도 기존 파일이 깨지지 않음)"""
    p = os.path.abspath(p); d = os.path.dirname(p)
    if d: os.makedirs(d, exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh: json.dump(obj, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, p)
def same_path(a, b): return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))
def load_paths():
    j = read_json(PATHS) or {}; o = {}
    for k in ("settings", "data"):
        v = j.get(k); o[k] = os.path.abspath(os.path.expanduser(v)) if isinstance(v, str) and v.strip() else FILE
    return o
def has_set(j): return isinstance(j, dict) and (j.get("lang") in TR or clean_theme(j.get("theme")) is not None or isinstance(j.get("ui"), dict))
def has_data(j): return isinstance(j, dict) and (any(isinstance(j.get(k), list) for k in ("tasks", "folders", "trash")) or isinstance(j.get("labels"), dict))
# ----- 마크다운
CHK = re.compile(r"^(\s*(?:[-*+]|\d+[.)])\s+\[)([ xX])(\])")
def toggle_chk(md, n):
    """마크다운 원문에서 n번째 체크박스(- [ ] / - [x])를 뒤집음 (코드 블록 안은 제외)"""
    ls = md.split("\n"); k = 0; fence = None
    for i, l in enumerate(ls):
        st = l.lstrip()
        if st.startswith("```") or st.startswith("~~~"):
            mk = st[:3]
            if fence is None: fence = mk
            elif mk == fence: fence = None
            continue
        if fence: continue
        m = CHK.match(l)
        if m:
            if k == n:
                ls[i] = l[:m.start(2)] + (" " if m.group(2) in "xX" else "x") + l[m.end(2):]
                return "\n".join(ls)
            k += 1
    return md
def _pid(e): return int(getattr(e, "value", e))
def md_render(doc, text, th):
    """QTextDocument에 마크다운(GitHub 방식: 표·체크박스·취소선 등) 적용 + 코드 블록 배경"""
    doc.setMarkdown(text)
    try:
        bg = QColor(mix(th["fg"], th["bg"], .1)); P = QTextFormat.Property; ks = (_pid(P.BlockCodeFence), _pid(P.BlockCodeLanguage)); b = doc.begin()
        while b.isValid():
            f = b.blockFormat()
            if f.nonBreakableLines() or any(f.hasProperty(k) for k in ks):
                f.setBackground(bg); QTextCursor(b).setBlockFormat(f)
            b = b.next()
    except Exception:
        pass
def hr(): f = QFrame(); f.setObjectName("hr"); f.setFixedHeight(1); return f
pill = lambda c: f"QComboBox{{background:{c};color:{ontext(c)};border:0;border-radius:12px;padding:2px 12px;font-weight:600}}"


class StayMenu(QMenu):
    """체크 항목을 눌러도 닫히지 않는 메뉴 (태그 여러 개 선택용)"""
    def mouseReleaseEvent(s, e):
        a = s.activeAction()
        if a and a.isEnabled() and a.isCheckable(): a.trigger(); return
        super().mouseReleaseEvent(e)


class EmojiDlg(QDialog):
    """폴더 아이콘 선택: 자주 쓰는 이모지 / 직접 입력 / 기본 아이콘"""
    def __init__(s, p, cur, L, title=None):
        super().__init__(p); s.setWindowTitle(title or L["icon"]); s.res = None; v = QVBoxLayout(s); g = QGridLayout(); g.setSpacing(4)
        for k, e in enumerate(EMO):
            b = QPushButton(e); b.setObjectName("ico"); b.setFixedSize(40, 40); b.clicked.connect(lambda _, e=e: s.pick(e)); g.addWidget(b, k // 8, k % 8)
        v.addLayout(g); h = QHBoxLayout()
        s.ed = QLineEdit(cur); s.ed.setPlaceholderText(L["emo"]); s.ed.setMaxLength(8); s.ed.returnPressed.connect(lambda: s.pick(s.ed.text().strip())); h.addWidget(s.ed, 1)
        ok = QPushButton(L["apply"]); ok.setObjectName("primary"); ok.clicked.connect(lambda: s.pick(s.ed.text().strip())); h.addWidget(ok); v.addLayout(h)
        df = QPushButton(L["deficon"]); df.clicked.connect(lambda: s.pick("")); v.addWidget(df)
    def pick(s, e): s.res = e; s.accept()


class RowDelegate(QStyledItemDelegate):
    """작업 표의 기본 델리게이트: 행 색상(배경 틴트 + 왼쪽 색 막대). 선택된 행은 틴트를 강조색 쪽으로 섞어 색이 가려지지 않게 함"""
    def __init__(s, w, p=None): super().__init__(p); s.w = w
    def paint(s, p, o, i):
        tc = getattr(s.w, "rowtint", {}).get(i.row())
        if not tc: return super().paint(p, o, i)
        sel = bool(o.state & QStyle.StateFlag.State_Selected); p.fillRect(o.rect, tc[1] if sel else tc[0])
        if i.column() == 0: p.fillRect(QRect(o.rect.x(), o.rect.y(), 4, o.rect.height()), tc[2])
        o2 = QStyleOptionViewItem(o); o2.state = o2.state & ~QStyle.StateFlag.State_Selected; super().paint(p, o2, i)


class NameDelegate(RowDelegate):
    enter = pyqtSignal(str)
    ren = False   # True면 '이름 바꾸기'(F2) 편집: Enter는 확정만 하고 새 작업을 만들지 않음
    def createEditor(s, p, o, i):
        e = QLineEdit(p); e.setProperty("tid", i.data(Qt.ItemDataRole.UserRole)); e.setProperty("ren", s.ren); s.ren = False; e.setPlaceholderText(s.ph); return e
    def eventFilter(s, ed, ev):
        if ev.type() == QEvent.Type.KeyPress and ev.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            ren = bool(ed.property("ren")); tid = ed.property("tid")
            s.commitData.emit(ed); s.closeEditor.emit(ed, QAbstractItemDelegate.EndEditHint.NoHint)
            if not ren: s.enter.emit(tid)
            return True
        return super().eventFilter(ed, ev)


class SepDelegate(QStyledItemDelegate):
    """완료함 구분 행의 윗변에 표 전체 너비로 긴 구분선을 그림"""
    def __init__(s, p, col): super().__init__(p); s.col = QColor(col)
    def paint(s, p, o, i):
        super().paint(p, o, i); p.save(); p.fillRect(o.rect.x(), o.rect.y(), o.rect.width(), 1, s.col); p.restore()


class DateDlg(QDialog):
    def __init__(s, p, val, L):
        super().__init__(p); s.setWindowTitle(L["due"]); s.res = None; v = QVBoxLayout(s); c = QCalendarWidget(); c.setGridVisible(False)
        c.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        if val: c.setSelectedDate(c.selectedDate().fromString(val, "yyyy-MM-dd"))
        c.clicked.connect(lambda d: (setattr(s, "res", d.toString("yyyy-MM-dd")), s.accept())); v.addWidget(c)
        b = QPushButton(L["clear"]); b.clicked.connect(lambda: (setattr(s, "res", ""), s.accept())); v.addWidget(b)


class Canvas(QWidget):
    def __init__(s, w): super().__init__(); s.w = w; s.hits = []; s.setMouseTracking(True)
    def mousePressEvent(s, e):
        try:
            pos = e.position()
            for r, i in s.hits:
                if r.contains(QPointF(pos.x(), pos.y())): return s.w.open_task(i)
        except Exception:
            pass
    def mouseMoveEvent(s, e):
        try:
            pos = e.position()
            s.setCursor(Qt.CursorShape.PointingHandCursor if any(r.contains(QPointF(pos.x(), pos.y())) for r, _ in s.hits) else Qt.CursorShape.ArrowCursor)
        except Exception:
            pass
    def wheelEvent(s, e):
        """Shift + 휠 = 가로 스크롤 (그 밖에는 바깥 스크롤 영역이 세로로 스크롤)"""
        a = s.parentWidget()
        while a is not None and not isinstance(a, QScrollArea): a = a.parentWidget()
        if a is not None and e.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            d = e.angleDelta().y() or e.angleDelta().x(); hb = a.horizontalScrollBar()
            hb.setValue(hb.value() - d); e.accept(); return
        e.ignore()
    def th(s): t = s.w.d["theme"]; fg = QColor(t["fg"]); mu = QColor(fg); mu.setAlpha(110); ln = QColor(fg); ln.setAlpha(28); return t, fg, mu, ln
    def chip(s, p, r, col, text, tid, alpha=255):
        c = QColor(col); c.setAlpha(alpha); p.setPen(Qt.PenStyle.NoPen); p.setBrush(c); p.drawRoundedRect(r, 6, 6); s.hits.append((r, tid))
        p.setPen(QColor("#fff")); p.drawText(r.adjusted(8, 0, -6, 0), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, QFontMetrics(p.font()).elidedText(text, Qt.TextElideMode.ElideRight, int(r.width() - 14)))


def addm(d, k):
    """d가 속한 달의 1일에서 k개월 이동한 날짜(1일)"""
    m = d.year * 12 + d.month - 1 + k
    return date(m // 12, m % 12 + 1, 1)


def periods(kind, o0, o1):
    """날짜 서수 o0 ~ o1 구간과 겹치는 기간 목록 [(시작 서수, 끝 서수(미포함), 시작 날짜)]. kind = day / month / quarter / year"""
    o0 = max(1, int(math.floor(o0))); o1 = int(math.ceil(o1)); out = []
    if kind == "day":
        return [(o, o + 1, date.fromordinal(o)) for o in range(o0, o1 + 1)]
    d = date.fromordinal(o0)
    if kind == "month": d = d.replace(day=1); step = 1
    elif kind == "quarter": d = date(d.year, (d.month - 1) // 3 * 3 + 1, 1); step = 3
    else: d = date(d.year, 1, 1); step = 12
    while d.toordinal() < o1:
        n = addm(d, step); out.append((d.toordinal(), n.toordinal(), d)); d = n
    return out


def mkscroll(wd):
    """뷰를 스크롤 영역으로 감쌈. 하단 가로 스크롤바는 항상 표시 (내용이 창보다 작으면 비활성)"""
    a = QScrollArea()
    a.setWidgetResizable(True)   # 창보다 작으면 창에 맞추고, 내용(최소 크기)이 크면 스크롤
    a.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)   # 하단 가로 스크롤바
    a.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)     # 우측 세로 스크롤바
    a.horizontalScrollBar().setSingleStep(30); a.verticalScrollBar().setSingleStep(30)
    a.setWidget(wd)
    return a


class Gantt(Canvas):
    """간트차트 (기간 막대). 왼쪽 작업명 열과 위쪽 날짜 머리글은 고정, 기간 영역만 가로로 끝없이 스크롤
    - 단위: 년 > 월 > 일.  Ctrl + 휠 위 = 더 세분화(년 → 월 → 일) / Ctrl + 휠 아래 = 더 크게(일 → 월 → 년). 마우스 위치의 날짜를 기준으로 확대·축소
    - ◀ ▶ = 이전/다음 달 (년 단위에서는 이전/다음 해) / 오늘 = 오늘로 이동
    - 하단 스크롤바 · Shift + 휠 · 터치패드 가로 스크롤 · 빈 곳 드래그 = 기간 이동 (끝에 가까워지면 범위가 자동으로 늘어나 계속 다음 달로 이어짐)
    - 화면 밖에 있는 막대는 가장자리 화살표로 표시, 클릭하면 그 막대로 이동"""
    LW, RH, HH = 220, 34, 54
    UNITS = ("year", "month", "day")                       # 큰 단위 → 작은 단위
    PPD = {"year": 0.55, "month": 4.0, "day": 32.0}        # 하루당 픽셀
    SPAN = {"year": 3650, "month": 730, "day": 180}        # 스크롤바가 화면 좌우로 미리 잡아 두는 범위(일)
    SUB = {"year": ("year", "quarter"), "month": ("year", "month"), "day": ("month", "day")}   # 머리글 (윗줄, 아랫줄)
    OMIN, OMAX = date(1900, 1, 1).toordinal(), date(2200, 1, 1).toordinal()
    def __init__(s, w):
        super().__init__(w); s.rows = []; s.vy = 0; s.jumps = []; s._sync = False; s._zacc = 0; s._pan = None; s.ubtn = {}; s.nb = []
        u = w.d["ui"].get("gunit"); s.unit = u if u in s.UNITS else "day"
        s.hb = QScrollBar(Qt.Orientation.Horizontal); s.vb = QScrollBar(Qt.Orientation.Vertical)
        s.hb.valueChanged.connect(s._hmoved); s.vb.valueChanged.connect(s._vmoved); s.hb.sliderReleased.connect(lambda: s.sync_bars(True))   # 손잡이를 놓으면 다시 가운데로 → 계속 이어서 이동
        s.left = 0.0; s.lo = s.hi = 0.0; s.home(False)
        s.setMinimumSize(s.LW + 160, s.HH + 80)
    # ----- 좌표
    def ppd(s): return s.PPD[s.unit]
    def vw(s): return max(s.width() - s.LW, 1)
    def X(s, o): return s.LW + (o - s.left) * s.ppd()
    def cur(s): return date.fromordinal(int(math.floor(s.left + 1e-6)))
    # ----- 이동
    def home(s, upd=True):
        """오늘이 보이는 위치로 (일 단위 = 이번 달 1일부터, 월 단위 = 2달 전부터, 년 단위 = 올해 1월부터)"""
        td = date.today()
        if s.unit == "day":
            f = td.replace(day=1); vw = s.vw() if s.width() > s.LW + 200 else 900
            o = f.toordinal() if (td - f).days * s.PPD["day"] < vw * 0.6 else td.toordinal() - 5
        elif s.unit == "month": o = addm(td, -2).toordinal()
        else: o = date(td.year, 1, 1).toordinal()
        s.go(o, upd)
    def go(s, o, upd=True):
        s.left = float(max(s.OMIN, min(s.OMAX, o)))
        if upd: s.sync_bars(True); s.upd_nav(); s.update()
    def mv(s, n):
        """◀ ▶: 일·월 단위 = 한 달씩, 년 단위 = 한 해씩. 화면 왼쪽 끝을 그 달(해)의 첫날에 맞춤"""
        d = s.cur(); yr = s.unit == "year"
        p0 = date(d.year, 1, 1) if yr else d.replace(day=1); st = 12 if yr else 1
        if n > 0: t = addm(p0, st)
        else: t = p0 if s.left > p0.toordinal() + 0.01 else addm(p0, -st)
        s.go(t.toordinal())
    def zoom(s, step, mx=None):
        """step > 0 = 더 세분화(년 → 월 → 일), step < 0 = 더 크게. mx(마우스 x) 위치의 날짜는 그대로 유지"""
        i = s.UNITS.index(s.unit); j = max(0, min(len(s.UNITS) - 1, i + step))
        if j == i: return
        mx = s.LW + s.vw() / 2 if mx is None else max(s.LW, min(s.width(), mx)); a = s.left + (mx - s.LW) / s.ppd()
        s.unit = s.UNITS[j]; s.w.d["ui"]["gunit"] = s.unit; s.w.save()
        s.go(a - (mx - s.LW) / s.ppd())
    def set_unit(s, u):
        if u in s.UNITS: s.zoom(s.UNITS.index(u) - s.UNITS.index(s.unit))
        s.upd_nav()
    # ----- 스크롤바 (가로 범위는 화면 좌우 SPAN 만큼만 잡아 두고, 끝에 가까워지면 다시 가운데로 맞춰 끝없이 이어지게 함)
    def sync_bars(s, recenter=False):
        p = s.ppd(); vw = s.vw(); sp = s.SPAN[s.unit]
        s.left = max(float(s.OMIN), min(float(s.OMAX), s.left))
        if recenter or s.left < s.lo or s.left + vw / p > s.hi:
            s.lo = max(float(s.OMIN), s.left - sp); s.hi = s.left + vw / p + sp
        ch = len(s.rows) * s.RH + 24; vh = max(s.height() - s.HH, 1)
        s._sync = True
        try:
            s.hb.setRange(0, max(0, int((s.hi - s.lo) * p - vw))); s.hb.setPageStep(int(vw)); s.hb.setSingleStep(max(24, int(p)))
            s.hb.setValue(int(round((s.left - s.lo) * p)))
            s.vb.setRange(0, max(0, ch - vh)); s.vb.setPageStep(vh); s.vb.setSingleStep(s.RH)
            s.vy = max(0, min(int(s.vy), s.vb.maximum())); s.vb.setValue(s.vy)
        finally:
            s._sync = False
    def _hmoved(s, v):
        if s._sync: return
        s.left = s.lo + v / s.ppd(); hb = s.hb; ps = hb.pageStep() // 2
        if (v < ps or v > hb.maximum() - ps) and not hb.isSliderDown(): s.sync_bars(True)   # 끝에 가까워지면 범위를 다시 잡아 끝없이 이어짐
        s.upd_nav(); s.update()
    def _vmoved(s, v):
        if s._sync: return
        s.vy = v; s.update()
    def resizeEvent(s, e):
        super().resizeEvent(e); s.sync_bars(); s.upd_nav()
    def prep(s):
        try:
            w = s.w; s.rows = [(t, w.rng(t)) for t in w.order(w.vis()) if w.rng(t)]
        except Exception:
            s.rows = []
        try: s.sync_bars(); s.upd_nav()
        except Exception: pass
        s.update()
    # ----- 상단 이동 막대 + 스크롤바를 붙인 화면
    def pane(s):
        L = s.w.L; box = QWidget(); v = QVBoxLayout(box); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(8)
        nav = QHBoxLayout(); nav.setSpacing(6)
        for tx, n in (("◀", -1), ("▶", 1)):
            b = QPushButton(tx); b.clicked.connect(lambda _, n=n: s.mv(n)); nav.addWidget(b); s.nb.append(b)
        b = QPushButton(L["g_today"]); b.clicked.connect(lambda: s.home()); nav.addWidget(b)
        s.lab = QLabel(); s.lab.setObjectName("title"); nav.addSpacing(6); nav.addWidget(s.lab); nav.addStretch()
        hint = QLabel(L["g_hint"]); hint.setObjectName("mu"); hint.setToolTip(L["g_tip"]); nav.addWidget(hint); nav.addSpacing(8)
        s._grp = QButtonGroup(box); s._grp.setExclusive(True)
        for u in s.UNITS:
            b = QPushButton(L["g_" + u]); b.setObjectName("seg"); b.setCheckable(True); b.setToolTip(L["g_tip"])
            s._grp.addButton(b); b.clicked.connect(lambda _, u=u: s.set_unit(u)); nav.addWidget(b); s.ubtn[u] = b
        v.addLayout(nav)
        g = QGridLayout(); g.setContentsMargins(0, 0, 0, 0); g.setSpacing(0)
        g.addWidget(s, 0, 0); g.addWidget(s.vb, 0, 1); g.addWidget(s.hb, 1, 0)
        v.addLayout(g, 1); s.upd_nav()
        return box
    def upd_nav(s):
        try:
            L = s.w.L; a = s.cur(); b = date.fromordinal(int(min(s.OMAX, s.left + s.vw() / s.ppd())))
            if s.unit == "day": tx = f"{a.year}.{a.month:02d}"
            elif s.unit == "month": tx = f"{a.year}.{a.month:02d} – {b.year}.{b.month:02d}"
            else: tx = f"{a.year} – {b.year}"
            if getattr(s, "lab", None): s.lab.setText(tx)
            for u, bt in s.ubtn.items(): bt.setChecked(u == s.unit)
            if len(s.nb) == 2:
                yr = s.unit == "year"; s.nb[0].setToolTip(L["g_py"] if yr else L["g_pm"]); s.nb[1].setToolTip(L["g_ny"] if yr else L["g_nm"])
        except Exception:
            pass
    # ----- 마우스 / 휠
    def wheelEvent(s, e):
        m = e.modifiers(); dx, dy = e.angleDelta().x(), e.angleDelta().y()
        if m & Qt.KeyboardModifier.ControlModifier:   # Ctrl + 휠 = 단위 변경 (위 = 세분화, 아래 = 크게)
            s._zacc += dy
            if abs(s._zacc) >= 120:
                st = 1 if s._zacc > 0 else -1; s._zacc = 0; s.zoom(st, e.position().x())
            e.accept(); return
        if abs(dx) > abs(dy) or m & Qt.KeyboardModifier.ShiftModifier:   # 가로 = 기간 이동
            d = dx if abs(dx) > abs(dy) else dy; s.hb.setValue(s.hb.value() - d)
        else:
            s.vb.setValue(s.vb.value() - dy)
        e.accept()
    def mousePressEvent(s, e):
        try:
            pos = e.position()
            if e.button() != Qt.MouseButton.LeftButton: return
            for r, o in s.jumps:   # 화면 밖 막대 화살표 → 그 막대로 이동
                if r.contains(pos): return s.go(o - s.vw() * 0.1 / s.ppd())
            for r, i in s.hits:
                if r.contains(pos): return s.w.open_task(i)
            if pos.x() > s.LW:   # 빈 곳 드래그 = 이동
                s._pan = (pos.x(), pos.y(), s.left, s.vy); s.setCursor(Qt.CursorShape.ClosedHandCursor)
        except Exception:
            pass
    def mouseMoveEvent(s, e):
        try:
            pos = e.position()
            if s._pan:
                x0, y0, l0, v0 = s._pan; s.left = l0 - (pos.x() - x0) / s.ppd(); s.vy = int(v0 - (pos.y() - y0))
                s.sync_bars(); s.upd_nav(); s.update(); return
            if any(r.contains(pos) for r, _ in s.hits + s.jumps): s.setCursor(Qt.CursorShape.PointingHandCursor)
            elif pos.x() > s.LW and pos.y() > s.HH: s.setCursor(Qt.CursorShape.OpenHandCursor)
            else: s.setCursor(Qt.CursorShape.ArrowCursor)
        except Exception:
            pass
    def mouseReleaseEvent(s, e):
        s._pan = None; s.setCursor(Qt.CursorShape.ArrowCursor)
    # ----- 그리기
    def paintEvent(s, e):
        try:
            p = QPainter(s); p.setRenderHint(QPainter.RenderHint.Antialiasing); t, fg, mu, ln = s.th(); s.hits = []; s.jumps = []
            W, H = s.width(), s.height(); LW, HH, RH = s.LW, s.HH, s.RH; pp = s.ppd(); w = s.w; L = w.L
            p.fillRect(s.rect(), QColor(t["bg"])); bd = QColor(mix(t["fg"], t["bg"], .14)); hd = QColor(t["panel"]); ac = QColor(t["accent"])
            strong = QColor(fg); strong.setAlpha(55); red = QColor("#ef4444"); loc = QLocale(w.d["lang"])
            f = QFont(p.font()); fb = QFont(f); fb.setBold(True); fs = QFont(f); fs.setPointSize(max(f.pointSize() - 1, 7)); fm = QFontMetrics(f); fms = QFontMetrics(fs)
            o0 = s.left; o1 = s.left + s.vw() / pp; td = date.today().toordinal()
            top, sub = s.SUB[s.unit]; tps = periods(top, o0, o1); sps = periods(sub, o0, o1)
            # 1) 기간 영역: 머리글 배경 · 주말 / 이번 달(분기) 강조 · 격자선 · 머리글 글자
            p.save(); p.setClipRect(QRectF(LW, 0, W - LW, H))
            p.fillRect(QRectF(LW, 0, W - LW, HH), hd)
            for a, b, d in sps:
                x = s.X(a); cw = (b - a) * pp
                if s.unit == "day" and d.weekday() >= 5: p.fillRect(QRectF(x, HH, cw, H - HH), ln)
                elif s.unit != "day" and a <= td < b: c = QColor(ac); c.setAlpha(20); p.fillRect(QRectF(x, HH, cw, H - HH), c)
                p.setPen(QPen(ln, 1)); p.drawLine(QPointF(x, HH / 2), QPointF(x, H))
                if s.unit == "day": tx = str(d.day)
                elif s.unit == "month": tx = loc.monthName(d.month, QLocale.FormatType.ShortFormat)
                else: tx = f"Q{(d.month - 1) // 3 + 1}"
                rr = QRectF(x, HH / 2, cw, HH / 2); p.setFont(fs)
                if fms.horizontalAdvance(tx) + 4 > cw: continue
                if a <= td < b:
                    if s.unit == "day":
                        p.setPen(Qt.PenStyle.NoPen); p.setBrush(ac); p.drawRoundedRect(QRectF(x + 3, HH / 2 + 3, cw - 6, HH / 2 - 7), 6, 6); p.setPen(QColor(ontext(t["accent"])))
                    else: p.setPen(ac)
                else: p.setPen(mu if (s.unit == "day" and d.weekday() >= 5) else fg)
                p.drawText(rr, Qt.AlignmentFlag.AlignCenter, tx)
            p.setFont(fb)
            for a, b, d in tps:
                xs = s.X(a); xe = s.X(b); p.setPen(QPen(strong, 1)); p.drawLine(QPointF(xs, 0), QPointF(xs, H))
                tx = f"{d.year}.{d.month:02d}" if top == "month" else f"{d.year}"
                x1 = max(xs, LW) + 8; avail = xe - x1 - 4   # 윗줄 글자는 화면 왼쪽 끝에 붙어 따라감
                if avail > 24:
                    p.setPen(ac); p.drawText(QRectF(x1, 0, avail, HH / 2), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, QFontMetrics(fb).elidedText(tx, Qt.TextElideMode.ElideRight, int(avail)))
            p.setFont(f); p.restore()
            # 2) 작업 행: 왼쪽 작업명(고정) + 기간 막대
            p.save(); p.setClipRect(QRectF(0, HH, W, H - HH))
            r0 = max(0, int(s.vy // RH)); r1 = min(len(s.rows), int((s.vy + H) // RH) + 1)
            for r in range(r0, r1):
                x, (a, b) = s.rows[r]; y = HH + r * RH - s.vy; done = w.is_done(x)
                p.setPen(QPen(ln, 1)); p.drawLine(QPointF(0, y + RH), QPointF(W, y + RH))
                c = QColor(w.tcol(x)); c.setAlpha(110 if done else 255); name = x["name"] or "—"
                p.save(); p.setClipRect(QRectF(LW, HH, W - LW, H - HH))
                bx = s.X(a.toordinal()); bw = max(((b - a).days + 1) * pp, 6); g = 2 if pp >= 16 else 0
                rc = QRectF(bx + g, y + 7, bw - 2 * g, RH - 14)
                if rc.right() < LW:   # 화면 왼쪽 밖 → ◀ 표시
                    p.setPen(Qt.PenStyle.NoPen); p.setBrush(c); cy = y + RH / 2
                    p.drawPolygon(QPolygonF([QPointF(LW + 6, cy), QPointF(LW + 14, cy - 6), QPointF(LW + 14, cy + 6)])); s.jumps.append((QRectF(LW, y + 4, 22, RH - 8), a.toordinal()))
                elif rc.left() > W:   # 화면 오른쪽 밖 → ▶ 표시
                    p.setPen(Qt.PenStyle.NoPen); p.setBrush(c); cy = y + RH / 2
                    p.drawPolygon(QPolygonF([QPointF(W - 6, cy), QPointF(W - 14, cy - 6), QPointF(W - 14, cy + 6)])); s.jumps.append((QRectF(W - 22, y + 4, 22, RH - 8), a.toordinal()))
                else:
                    p.setPen(Qt.PenStyle.NoPen); p.setBrush(c); p.drawRoundedRect(rc, 6, 6)
                    vis = rc.intersected(QRectF(LW, 0, W - LW, H)); s.hits.append((vis, x["id"]))
                    if vis.width() >= fm.horizontalAdvance(name) + 16:   # 막대 안에 이름 (보이는 부분 왼쪽에 붙음)
                        p.setPen(QColor(ontext(c.name()))); p.drawText(vis.adjusted(8, 0, -6, 0), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, name)
                    elif rc.right() + 6 < W:
                        p.setPen(mu); p.drawText(QRectF(rc.right() + 6, y, 400, RH), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, name)
                p.restore()
                p.fillRect(QRectF(0, y, LW, RH), QColor(t["bg"])); p.setPen(QPen(ln, 1)); p.drawLine(QPointF(0, y + RH), QPointF(LW, y + RH))
                nm = (w.pin_e() + " " if x["pin"] else "") + name; p.setFont(f); p.setPen(mu if done else fg)
                p.drawText(QRectF(10, y, LW - 20, RH), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, fm.elidedText(nm, Qt.TextElideMode.ElideRight, LW - 20))
                s.hits.append((QRectF(10, y + 6, min(fm.horizontalAdvance(nm) + 6, LW - 20), RH - 12), x["id"]))
            p.restore()
            # 3) 오늘 선
            tx = s.X(td + 0.5)
            if LW <= tx <= W:
                p.setPen(QPen(red, 2)); p.drawLine(QPointF(tx, HH - 2), QPointF(tx, H)); p.setPen(Qt.PenStyle.NoPen); p.setBrush(red); p.drawEllipse(QPointF(tx, HH - 2), 3.5, 3.5)
            # 4) 고정 영역 테두리 · 왼쪽 위 칸
            p.fillRect(QRectF(0, 0, LW, HH), hd); p.setPen(mu); p.setFont(fs)
            p.drawText(QRectF(10, HH / 2, LW - 20, HH / 2), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, L["cols"][0] if L.get("cols") else "")
            p.setPen(QPen(bd, 1)); p.drawLine(QPointF(0, HH), QPointF(W, HH)); p.drawLine(QPointF(LW, 0), QPointF(LW, H)); p.setFont(f)
            if not s.rows:
                p.setPen(mu); p.drawText(QRectF(LW, HH, W - LW, H - HH), Qt.AlignmentFlag.AlignCenter, L["empty"])
        except Exception:
            pass


class CalGrid(Canvas):
    """캘린더: 아래로 스크롤하면 다음 달이 끊김 없이 이어지는 주 단위 무한 스크롤
    - 2일 이상 일정은 주 안에서 한 줄짜리 막대로 이어지고(주를 넘기면 다음 주에서 이어짐), 막대 색 = 행 색상(없으면 우선순위 색)
    - 날짜 칸의 빈 곳(날짜 숫자 줄 · 막대 오른쪽 여백 포함)을 클릭하면 그 날짜로 새 작업 추가
    - 칸이 꽉 차 있어도 날짜 숫자 줄 / 막대 오른쪽 끝 여백을 클릭하면 추가됨 (마우스를 올리면 + 표시)"""
    HH, LH, STRIP, SPAN = 30, 21, 12, 400
    OW0 = (date(1900, 1, 1).toordinal() - 1) // 7
    OW1 = (date(2200, 1, 1).toordinal() - 1) // 7
    def __init__(s, w):
        super().__init__(w); s._sync = False; s.hov = None; s.more = []
        s.vb = QScrollBar(Qt.Orientation.Vertical); s.vb.valueChanged.connect(s._vmoved); s.vb.sliderReleased.connect(lambda: s.sync_bars(True))
        s.top = float(s.wk(w.cal)); s.lo = s.hi = s.top; s.setMinimumHeight(200)
    @staticmethod
    def wk(d): return (d.toordinal() - 1) // 7          # 월요일 시작 주 번호
    def rh(s): return max(84.0, (s.height() - s.HH) / 6.0)
    def sync_bars(s, recenter=False):
        rh = s.rh(); vh = max(s.height() - s.HH, 1); vis = vh / rh
        s.top = max(float(s.OW0), min(float(s.OW1) - vis, s.top))
        if recenter or s.top < s.lo or s.top + vis > s.hi: s.lo = max(float(s.OW0), s.top - s.SPAN); s.hi = min(float(s.OW1), s.top + vis + s.SPAN)
        s._sync = True
        try:
            s.vb.setRange(0, max(0, int((s.hi - s.lo) * rh - vh))); s.vb.setPageStep(int(vh)); s.vb.setSingleStep(max(int(rh / 3), 10)); s.vb.setValue(int(round((s.top - s.lo) * rh)))
        finally:
            s._sync = False
    def _vmoved(s, v):
        if s._sync: return
        s.top = s.lo + v / s.rh(); vb = s.vb; ps = vb.pageStep() // 2
        if (v < ps or v > vb.maximum() - ps) and not vb.isSliderDown(): s.sync_bars(True)   # 끝에 가까워지면 범위를 다시 잡아 끝없이 이어짐
        s.upd_month(); s.update()
    def upd_month(s):
        """화면 가운데쯤에 보이는 달을 상단 제목에 반영"""
        try:
            o = (int(round(s.top)) + 1) * 7 + 1 + 3; m = date.fromordinal(max(1, o)).replace(day=1)
            if m != s.w.cal: s.w.cal = m; s.w.cl.setText(f"{m.year}.{m.month:02d}")
        except Exception:
            pass
    def goto(s, d):
        s.top = float(s.wk(d)); s.sync_bars(True); s.upd_month(); s.update()
    def resizeEvent(s, e): super().resizeEvent(e); s.sync_bars()
    def wheelEvent(s, e):
        if e.modifiers() & Qt.KeyboardModifier.ShiftModifier: return super().wheelEvent(e)   # Shift + 휠 = 가로 스크롤
        s.vb.setValue(s.vb.value() - e.angleDelta().y()); e.accept()
    def dayat(s, pos):
        if pos.y() <= s.HH: return None
        wi = int(math.floor(s.top + (pos.y() - s.HH) / s.rh())); c = min(6, max(0, int(pos.x() // (s.width() / 7)))); o = wi * 7 + 1 + c
        return o if 1 <= o <= date.max.toordinal() else None
    def mousePressEvent(s, e):
        try:
            if e.button() != Qt.MouseButton.LeftButton: return
            pos = e.position()
            for r, i in s.hits:
                if r.contains(pos): return s.w.open_task(i)
            if any(r.contains(pos) for r in s.more): return
            o = s.dayat(pos)
            if o: iso = date.fromordinal(o).isoformat(); s.w.add(start=iso, end=iso)   # 빈 곳 클릭 → 그 날짜에 새 작업
        except Exception:
            pass
    def mouseMoveEvent(s, e):
        try:
            pos = e.position(); o = s.dayat(pos)
            if o != s.hov: s.hov = o; s.update()
            if any(r.contains(pos) for r, _ in s.hits): s.setCursor(Qt.CursorShape.PointingHandCursor)
            elif o: s.setCursor(Qt.CursorShape.CrossCursor)
            else: s.setCursor(Qt.CursorShape.ArrowCursor)
        except Exception:
            pass
    def leaveEvent(s, e):
        if s.hov is not None: s.hov = None; s.update()
    def paintEvent(s, e):
        try:
            p = QPainter(s); p.setRenderHint(QPainter.RenderHint.Antialiasing); t, fg, mu, ln = s.th(); s.hits = []; s.more = []; w = s.w
            W, H, HH, LH, STRIP = s.width(), s.height(), s.HH, s.LH, s.STRIP; p.fillRect(s.rect(), QColor(t["bg"]))
            cw = W / 7; rh = s.rh(); top = s.top; w0 = int(math.floor(top)); y0 = HH - (top - w0) * rh; n = int((H - HH) / rh) + 2
            loc = QLocale(w.d["lang"]); f = QFont(p.font()); fb = QFont(f); fb.setBold(True); fs = QFont(f); fs.setPointSize(max(f.pointSize() - 1, 7)); fm = QFontMetrics(f); fmb = QFontMetrics(fb); fms = QFontMetrics(fs)
            tdo = date.today().toordinal(); ac = QColor(t["accent"]); bd = QColor(mix(t["fg"], t["bg"], .14))
            tint = QColor(fg); tint.setAlpha(9); hovc = QColor(fg); hovc.setAlpha(16); tdc = QColor(ac); tdc.setAlpha(26); MAXO = date.max.toordinal()
            spans = []   # (작업, 시작 서수, 끝 서수, 시작/종료일이 있는가, 마감 서수)
            for x in w.vis():
                r = w.rng(x)
                if not r: continue
                due = None
                if x.get("due"):
                    try: due = date.fromisoformat(x["due"]).toordinal()
                    except Exception: due = None
                spans.append((x, r[0].toordinal(), r[1].toordinal(), bool(x.get("start") or x.get("end")), due))
            p.save(); p.setClipRect(QRectF(0, HH, W, H - HH))
            for r in range(n):
                wi = w0 + r; y = y0 + r * rh; m = wi * 7 + 1
                if m < 1 or m + 6 > MAXO: continue
                # 1) 칸 바탕 · 격자 · 날짜 숫자 (달이 바뀌는 곳은 홀/짝 달 바탕색으로 구분, 1일에는 월 표시)
                for c in range(7):
                    o = m + c; d = date.fromordinal(o); x0 = c * cw; rc = QRectF(x0, y, cw, rh)
                    if d.month % 2 == 0: p.fillRect(rc, tint)
                    if o == tdo: p.fillRect(rc, tdc)
                    if s.hov == o: p.fillRect(rc, hovc)
                    p.setPen(QPen(ln, 1)); p.drawLine(QPointF(x0, y), QPointF(x0, y + rh))
                    first = d.day == 1; txt = loc.toString(QDate(d.year, d.month, 1), "MMM d") if first else str(d.day); fx = fmb if first else fm
                    lw = max(22.0, fx.horizontalAdvance(txt) + 14); lab = QRectF(x0 + 4, y + 4, lw, 22); p.setFont(fb if first else f)
                    if o == tdo: p.setPen(Qt.PenStyle.NoPen); p.setBrush(ac); p.drawRoundedRect(lab, 11, 11); p.setPen(QColor(ontext(t["accent"])))
                    else: p.setPen(ac if first else (mu if c >= 5 else fg))
                    p.drawText(lab, Qt.AlignmentFlag.AlignCenter, txt); p.setFont(f)
                    if s.hov == o: p.setPen(mu); p.drawText(QRectF(x0 + cw - 24, y + 4, 20, 22), Qt.AlignmentFlag.AlignCenter, "+")   # 이 칸을 클릭하면 새 작업
                p.setPen(QPen(ln, 1)); p.drawLine(QPointF(0, y + rh), QPointF(W, y + rh))
                # 2) 이 주의 일정 막대: 여러 날 일정은 한 줄로 이어짐 (주를 넘으면 다음 주에서 이어서 표시)
                items = []   # (시작 칸, 끝 칸, 앞에서 이어짐?, 뒤로 이어짐?, 작업, 마감 표시?)
                for x, a, b, hasr, due in spans:
                    if hasr:
                        if not (b < m or a > m + 6): items.append((max(a, m) - m, min(b, m + 6) - m, a < m, b > m + 6, x, False))
                        if due is not None and not (a <= due <= b) and m <= due <= m + 6: items.append((due - m, due - m, False, False, x, True))
                    elif m <= a <= m + 6: items.append((a - m, a - m, False, False, x, True))
                items.sort(key=lambda it: (it[0], -(it[1] - it[0]), it[4]["name"]))
                lane_end = []; more = [0] * 7; mx = max(int((rh - 32) // LH), 1)
                for ca, cb, cl, cr, x, isd in items:
                    ln_i = next((k for k, v in enumerate(lane_end) if v < ca), len(lane_end))
                    if ln_i == len(lane_end): lane_end.append(cb)
                    else: lane_end[ln_i] = cb
                    if ln_i >= mx:
                        for c in range(ca, cb + 1): more[c] += 1
                        continue
                    ry = y + 30 + ln_i * LH; bx0 = ca * cw + (0 if cl else 3); bx1 = (cb + 1) * cw - (0 if cr else STRIP)   # 끝나는 칸은 오른쪽 여백을 남겨 클릭으로 추가 가능
                    rect = QRectF(bx0, ry, max(bx1 - bx0, 8), LH - 2); col = w.tcol(x); c0 = QColor(col); c0.setAlpha(120 if w.is_done(x) else 255)
                    path = QPainterPath(); path.setFillRule(Qt.FillRule.WindingFill); path.addRoundedRect(rect, 5, 5)
                    if cl: path.addRect(QRectF(rect.x(), rect.y(), 8, rect.height()))
                    if cr: path.addRect(QRectF(rect.right() - 8, rect.y(), 8, rect.height()))
                    p.setPen(Qt.PenStyle.NoPen); p.setBrush(c0); p.drawPath(path); s.hits.append((rect, x["id"]))
                    p.setFont(fs); p.setPen(QColor(ontext(col))); nm = ("◆ " if isd else "") + (x["name"] or "—")
                    p.drawText(rect.adjusted(6, 0, -4, 0), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, fms.elidedText(nm, Qt.TextElideMode.ElideRight, int(max(rect.width() - 10, 8))))
                    due = next((sp[4] for sp in spans if sp[0] is x), None)
                    if not isd and due is not None and m <= due <= m + 6 and ca <= due - m <= cb and x.get("due") and (x.get("start") or x.get("end")):
                        gx = min((due - m + 1) * cw - 14, rect.right() - 12)
                        if gx > rect.x() + 6: p.drawText(QRectF(gx, ry, 12, LH - 2), Qt.AlignmentFlag.AlignCenter, "◆")   # 범위 안의 마감일
                    p.setFont(f)
                p.setFont(fs)
                for c in range(7):
                    if more[c]:
                        rr = QRectF(c * cw + cw - 66, y + 5, 40, 18); p.setPen(mu); p.drawText(rr, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, f"+{more[c]}"); s.more.append(rr)
                p.setFont(f)
            p.restore()
            # 3) 요일 머리글 (고정)
            p.fillRect(QRectF(0, 0, W, HH), QColor(t["bg"]))
            for c in range(7): p.setPen(mu); p.drawText(QRectF(c * cw, 0, cw, HH), Qt.AlignmentFlag.AlignCenter, loc.dayName(c + 1, QLocale.FormatType.ShortFormat))
            p.setPen(QPen(bd, 1)); p.drawLine(QPointF(0, HH), QPointF(W, HH))
        except Exception:
            pass


class TLView(Canvas):
    """타임라인 (사건의 흐름). 간트차트가 '기간'을 막대로 보여 준다면, 타임라인은 '언제 무슨 일이 있었고 / 있을지'를 시간 순 사건으로 보여 줌
    - 사건: ▶ 시작 · ■ 종료 · ◆ 마감 · ✓ 완료(완료한 실제 날짜) — 작업 하나가 여러 사건을 만들 수 있음
    - 가운데 세로 축을 따라 위 = 과거, 아래 = 미래. 월 제목 → 날짜 → 사건 카드(좌우 번갈아)
    - 오늘 기준선(오늘 사건이 없어도 표시), 지난 사건은 흐리게, 기한이 지난 마감은 빨간색
    - 상단: 사건 종류 켜기/끄기, 오늘로 이동, 요약(기한 지남 · 오늘 · 7일 이내). 제목 클릭 = 편집 사이드바"""
    CW, GAP, CH, STEP = 300, 34, 58, 38   # 카드 너비 / 축과 카드 사이 / 카드 높이 / 다음 카드까지 세로 간격(좌우 번갈아 겹쳐 배치)
    KINDS = ("start", "end", "due", "done")
    SYM = {"start": "▶", "end": "■", "due": "◆", "done": "✓"}
    def __init__(s, w):
        super().__init__(w); s.ev = []; s.blocks = []; s.ty = 0; s.H = 200; s.area = None; s.btn = {}; s.sum = None
    def on(s, k): return bool((s.w.d["ui"].get("tlf") or {}).get(k, True))
    def tog(s, k, v):
        f = dict(s.w.d["ui"].get("tlf") or {}); f[k] = bool(v); s.w.d["ui"]["tlf"] = f; s.w.save(); s.prep()
    def pane(s):
        L = s.w.L; box = QWidget(); v = QVBoxLayout(box); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(8)
        nav = QHBoxLayout(); nav.setSpacing(6)
        b = QPushButton(L["tl_goto"]); b.clicked.connect(lambda: s.to_today()); nav.addWidget(b); nav.addSpacing(10)
        for k in s.KINDS:
            b = QPushButton(s.SYM[k] + "  " + L["tl_" + k]); b.setObjectName("seg"); b.setCheckable(True); b.setChecked(s.on(k))
            b.toggled.connect(lambda v, k=k: s.tog(k, v)); nav.addWidget(b); s.btn[k] = b
        nav.addStretch(); s.sum = QLabel(); s.sum.setObjectName("mu"); nav.addWidget(s.sum)
        v.addLayout(nav); s.area = mkscroll(s); v.addWidget(s.area, 1)
        return box
    def to_today(s):
        """오늘 기준선이 화면 위쪽 1/4 쯤에 오도록 스크롤"""
        try:
            if s.area: vb = s.area.verticalScrollBar(); vb.setValue(max(0, int(s.ty - s.area.viewport().height() * 0.25)))
        except Exception:
            pass
    def rel(s, d, td):
        L = s.w.L; n = (d - td).days
        return L["rel0"] if n == 0 else L["relp1"] if n == 1 else L["relm1"] if n == -1 else L["relf"].format(n=n) if n > 0 else L["relb"].format(n=-n)
    def prep(s):
        try:
            w = s.w; td = date.today(); ev = []; vs = w.vis()
            for x in vs:
                for k, val in (("start", x["start"]), ("end", x["end"] if x["end"] != x["start"] else ""), ("due", x["due"])):
                    if val and s.on(k):
                        try: ev.append((date.fromisoformat(val), s.KINDS.index(k), k, x))
                        except Exception: pass
                if s.on("done") and w.is_done(x) and x.get("done_at"):
                    try: ev.append((date.fromtimestamp(float(x["done_at"])), 3, "done", x))
                    except Exception: pass
            ev.sort(key=lambda e: (e[0], e[1], nat(e[3]["name"])))
            s.ev = ev; s.lay(td)
            if s.sum is not None:
                act = [x for x in vs if not w.is_done(x)]
                o = sum(1 for x in act if w.overdue(x)); tdn = td.isoformat()
                tn = sum(1 for x in act if tdn in (x["due"], x["start"]))
                k = sum(1 for x in act if x["due"] and tdn < x["due"] <= (td + timedelta(7)).isoformat())
                s.sum.setText(w.L["tl_sum"].format(o=o, t=tn, k=k))
        except Exception:
            s.ev = []; s.blocks = []
        s.update()
    def lay(s, td):
        """세로 배치 계산 (너비와 무관한 y 좌표만). blocks: ('month', y, 날짜) / ('day', y, 날짜, 오늘?) / ('today', y) / ('ev', y, 쪽, 사건)"""
        B = []; y = 24; cm = None; side = 0; tdone = False; i = 0; ev = s.ev; s.ty = 0
        def month(d):
            nonlocal y, cm
            if (d.year, d.month) != cm: cm = (d.year, d.month); B.append(("month", y, d)); y += 50
        while i < len(ev):
            d = ev[i][0]
            if not tdone and d > td:
                month(td); s.ty = y; B.append(("today", y)); y += 52; tdone = True
            month(d)
            if d == td: tdone = True; s.ty = y
            B.append(("day", y, d, d == td)); y += 40; last = y
            while i < len(ev) and ev[i][0] == d:
                B.append(("ev", y, side, ev[i])); side ^= 1; last = y; y += s.STEP; i += 1
            y = last + s.CH + 22
        if not tdone and ev:
            month(td); s.ty = y; B.append(("today", y)); y += 52
        s.blocks = B; s.H = y + 40
        MW = 2 * (s.CW + s.GAP) + 40
        if s.minimumHeight() != s.H or s.minimumWidth() != MW: s.setMinimumSize(MW, s.H); s.updateGeometry()
    def kcol(s, k, x, d, td, t):
        if k == "start": return QColor(t["accent"])
        if k == "end": return QColor(mix(t["fg"], t["bg"], .55))
        if k == "done": return QColor("#10b981")
        return QColor("#ef4444") if (d < td and not s.w.is_done(x)) else QColor(s.w.tcol(x))
    def dot(s, p, k, c, cx, cy, bg):
        """축 위 사건 표시: 시작 = 원 / 종료 = 사각형 / 마감 = 마름모 / 완료 = 체크 원"""
        p.setPen(QPen(QColor(bg), 3)); p.setBrush(c)
        if k == "end": p.drawRect(QRectF(cx - 6, cy - 6, 12, 12))
        elif k == "due": p.drawPolygon(QPolygonF([QPointF(cx, cy - 8), QPointF(cx + 8, cy), QPointF(cx, cy + 8), QPointF(cx - 8, cy)]))
        else: p.drawEllipse(QPointF(cx, cy), 7.5, 7.5)
        if k == "done":
            p.setPen(QPen(QColor("#fff"), 2)); p.drawPolyline(QPolygonF([QPointF(cx - 3.5, cy), QPointF(cx - 1, cy + 3), QPointF(cx + 4, cy - 3)]))
    def paintEvent(s, e):
        try:
            p = QPainter(s); p.setRenderHint(QPainter.RenderHint.Antialiasing); t, fg, mu, ln = s.th(); s.hits = []; w = s.w; L = w.L
            p.fillRect(s.rect(), QColor(t["bg"]))
            if not s.blocks:
                p.setPen(mu); p.drawText(s.rect().adjusted(40, 0, -40, 0), Qt.AlignmentFlag.AlignCenter.value | Qt.TextFlag.TextWordWrap.value, L["tl_empty"]); return
            W = s.width(); cx = W / 2; td = date.today(); loc = QLocale(w.d["lang"]); bd = QColor(mix(t["fg"], t["bg"], .14)); ac = QColor(t["accent"]); red = QColor("#ef4444")
            f = QFont(p.font()); fb = QFont(f); fb.setBold(True); fm_ = QFont(fb); fm_.setPointSize(f.pointSize() + 4); fs = QFont(f); fs.setPointSize(max(f.pointSize() - 1, 7))
            fmb, fms = QFontMetrics(fb), QFontMetrics(fs)
            ax = QColor(fg); ax.setAlpha(45); p.setPen(QPen(ax, 2)); p.drawLine(QPointF(cx, 12), QPointF(cx, s.H - 20))   # 시간 축
            def wd(d): return loc.dayName(d.isoweekday(), QLocale.FormatType.ShortFormat)
            def pill(y, tx, bgc, fgc, bc, font):
                fmx = QFontMetrics(font); pw = fmx.horizontalAdvance(tx) + 26; r = QRectF(cx - pw / 2, y, pw, 26)
                p.setPen(QPen(bc, 1)); p.setBrush(bgc); p.drawRoundedRect(r, 8, 8); p.setFont(font); p.setPen(fgc); p.drawText(r, Qt.AlignmentFlag.AlignCenter, tx)
            for b in s.blocks:
                k = b[0]; y = b[1]
                if k == "month":
                    d = b[2]; tx = f"{d.year}.{d.month:02d}"; p.setFont(fm_); tw = QFontMetrics(fm_).horizontalAdvance(tx) + 24
                    p.fillRect(QRectF(cx - tw / 2, y, tw, 36), QColor(t["bg"])); p.setPen(ac); p.drawText(QRectF(cx - tw / 2, y, tw, 36), Qt.AlignmentFlag.AlignCenter, tx)
                elif k == "day":
                    d, isT = b[2], b[3]; tx = f"{d.month:02d}.{d.day:02d} ({wd(d)})  ·  {s.rel(d, td)}"
                    if isT: pill(y, tx, ac, QColor(ontext(t["accent"])), ac, fb)
                    else: pill(y, tx, QColor(t["panel"]), mu if d < td else fg, bd, fs)
                elif k == "today":
                    pen = QPen(red, 1.5); pen.setStyle(Qt.PenStyle.DashLine); p.setPen(pen); p.drawLine(QPointF(16, y + 13), QPointF(W - 16, y + 13))
                    pill(y, f"{L['rel0']} · {td.month:02d}.{td.day:02d} ({wd(td)})  ·  {L['tl_none']}", QColor(t["bg"]), red, red, fb)
                else:
                    side, (d, _, kd, x) = b[2], b[3]; done = w.is_done(x); c = s.kcol(kd, x, d, td, t)
                    over = kd == "due" and d < td and not done; past = d < td and not over
                    rc = QRectF(cx - s.GAP - s.CW, y, s.CW, s.CH) if side == 0 else QRectF(cx + s.GAP, y, s.CW, s.CH); cy = y + s.CH / 2
                    p.setOpacity(.6 if past else 1.0)
                    p.setPen(QPen(ln, 1.5)); p.drawLine(QPointF(cx, cy), QPointF(rc.right() if side == 0 else rc.left(), cy))   # 축 → 카드 연결선
                    p.setPen(QPen(red if over else bd, 1)); p.setBrush(QColor(mix(x["color"], t["panel"], .25) if x.get("color") else t["panel"])); p.drawRoundedRect(rc.adjusted(.5, .5, -.5, -.5), 9, 9)
                    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor(w.tcol(x))); p.drawRoundedRect(QRectF(rc.x() + 1, rc.y() + 8, 4, s.CH - 16), 2, 2)   # 행 색상 띠 (색이 없으면 우선순위 색)
                    # 1행: [종류] 제목
                    x0 = rc.x() + 14; bt = s.SYM[kd] + " " + L["tl_" + kd]; p.setFont(fs); bw = fms.horizontalAdvance(bt)
                    p.setPen(c); p.drawText(QRectF(x0, y + 7, bw + 2, 22), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, bt)
                    nm = x["name"] or "—"; tx0 = x0 + bw + 8; tw = rc.right() - 12 - tx0; ff = QFont(fb); ff.setStrikeOut(done and kd != "done"); p.setFont(ff)
                    p.setPen(mu if (done and kd != "done") else fg); el = QFontMetrics(ff).elidedText(nm, Qt.TextElideMode.ElideRight, int(max(tw, 10)))
                    p.drawText(QRectF(tx0, y + 7, tw, 22), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, el)
                    s.hits.append((QRectF(tx0, y + 7, min(QFontMetrics(ff).horizontalAdvance(el) + 6, tw), 22), x["id"]))
                    # 2행: 설명 + 상태
                    if kd in ("start", "end") and w.rng(x):
                        a1, b1 = w.rng(x); meta = f"{a1.month:02d}.{a1.day:02d} → {b1.month:02d}.{b1.day:02d} · {L['ndays'].format(n=(b1 - a1).days + 1)}"
                    elif kd == "due": meta = (L["tl_over"] + " · " if over else "") + s.rel(d, td)
                    else:
                        try: meta = time.strftime("%H:%M", time.localtime(float(x["done_at"])))
                        except Exception: meta = ""
                    stn = w.lname("status", x["status"]); sc = w.lcol("status", x["status"]); sw_ = min(fms.horizontalAdvance(stn) + 14, 110)
                    sr = QRectF(rc.right() - 12 - sw_, y + 32, sw_, 18); p.setFont(fs)
                    p.setPen(red if over else mu); p.drawText(QRectF(x0, y + 31, sr.x() - x0 - 6, 20), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, fms.elidedText(meta, Qt.TextElideMode.ElideRight, int(max(sr.x() - x0 - 6, 10))))
                    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor(sc)); p.drawRoundedRect(sr, 6, 6); p.setPen(QColor(ontext(sc)))
                    p.drawText(sr, Qt.AlignmentFlag.AlignCenter, fms.elidedText(stn, Qt.TextElideMode.ElideRight, int(sw_ - 8)))
                    s.dot(p, kd, c, cx, cy, t["bg"]); p.setOpacity(1.0)
            p.setFont(f)
        except Exception:
            pass


class KeepView(Canvas):
    """Google Keep 스타일 카드: 제목 / 세부 내용 / 하단 한 줄 [중요도][진행상태][마감일]. 제목 클릭 = 편집 사이드바"""
    CW, G, P = 250, 14, 14
    def prep(s): s.lay(); s.update()
    def resizeEvent(s, e): super().resizeEvent(e); s.lay()
    def mdoc(s, x, tw, f):
        """카드 메모용 마크다운 문서 (메모·너비·글꼴·테마가 같으면 캐시 재사용)"""
        c = getattr(s, "_mdc", None)
        if c is None: c = s._mdc = {}
        th = s.w.d["theme"]; key = (x["memo"], tw, f.toString(), th["fg"], th["bg"]); hit = c.get(x["id"])
        if hit and hit[0] == key: return hit[1]
        d = QTextDocument(); d.setDefaultFont(f); d.setDocumentMargin(0); md_render(d, x["memo"].strip(), th); d.setTextWidth(tw)
        c[x["id"]] = (key, d); return d
    def fonts(s):
        s.ensurePolished(); f = QFont(s.font()); fb = QFont(f); fb.setBold(True); fb.setPointSize(f.pointSize() + 1); fs = QFont(f); fs.setPointSize(max(f.pointSize() - 2, 7)); return f, fb, fs
    WR = (Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop).value | Qt.TextFlag.TextWordWrap.value
    def lay(s):
        try:
            w = s.w; f, fb, fs = s.fonts(); fm, fmb, fms = QFontMetrics(f), QFontMetrics(fb), QFontMetrics(fs); vs = w.vis()
            items = w.order([x for x in vs if not w.is_done(x)]) + sorted([x for x in vs if w.is_done(x)], key=lambda x: -x.get("done_at", 0))
            W = max(s.width(), s.CW + 2 * s.G); n = max(1, int((W - s.G) // (s.CW + s.G))); cw = (W - s.G * (n + 1)) / n; tw = int(cw - 2 * s.P)
            hs = [float(s.G)] * n; s.cards = []; hits = []
            for x in items:
                ttw = tw - (24 if x["pin"] else 0)
                th = min(fmb.boundingRect(QRect(0, 0, ttw, 100000), s.WR, x["name"] or "—").height(), fmb.lineSpacing() * 3)
                mh = int(min(s.mdoc(x, tw, f).size().height() + 1, fm.lineSpacing() * 10)) if x["memo"].strip() else 0
                ch = fms.height() + 8; h = s.P + th + (8 + mh if mh else 0) + 12 + ch + s.P
                c = hs.index(min(hs)); rc = QRectF(s.G + c * (cw + s.G), hs[c], cw, h); s.cards.append((rc, x, th, mh, ch)); hs[c] += h + s.G
                # 제목 클릭 영역은 레이아웃 단계에서 한 번에 계산 (부분 다시 그리기와 무관하게 항상 전체 카드 유지)
                bw = fmb.boundingRect(QRect(0, 0, ttw, 100000), s.WR, x["name"] or "—").width()
                hits.append((QRectF(rc.x() + s.P, rc.y() + s.P, min(bw + 6, ttw), th), x["id"]))
            s.hits = hits
            H = int(max(hs)) + 10; MW = s.CW + 2 * s.G
            if s.minimumHeight() != H or s.minimumWidth() != MW: s.setMinimumSize(MW, H); s.updateGeometry()
        except Exception:
            s.cards = []; s.hits = []
    def paintEvent(s, e):
        try:
            # 주의: 여기서 s.hits를 비우지 않음. 사이드바 애니메이션 등으로 일부 영역만 다시 그려질 때
            #       보이는 카드만 클릭 영역에 남아 다른 카드 제목 클릭이 막히던 문제의 원인이었음
            p = QPainter(s); p.setRenderHint(QPainter.RenderHint.Antialiasing); t, fg, mu, ln = s.th(); w = s.w; p.fillRect(s.rect(), QColor(t["bg"]))
            if not getattr(s, "cards", None):
                p.setPen(mu); p.drawText(s.rect(), Qt.AlignmentFlag.AlignCenter, w.L["empty2"]); return
            f, fb, fs = s.fonts(); fms = QFontMetrics(fs); bd = QColor(mix(t["fg"], t["bg"], .14)); body = QColor(mix(t["fg"], t["bg"], .78)); td = date.today().isoformat(); red = QColor("#ef4444")
            for rc, x, th, mh, ch in s.cards:
                if not rc.intersects(QRectF(e.rect())): continue
                done = w.is_done(x); tw = rc.width() - 2 * s.P; y = rc.y() + s.P
                p.setPen(QPen(bd, 1)); p.setBrush(QColor(mix(x["color"], t["panel"], .25) if x.get("color") else t["panel"])); p.drawRoundedRect(rc.adjusted(.5, .5, -.5, -.5), 10, 10)   # 행 색상 = 카드 색
                # 제목 (클릭 영역)
                ttw = tw - (24 if x["pin"] else 0); tr = QRectF(rc.x() + s.P, y, ttw, th); ff = QFont(fb); ff.setStrikeOut(done); p.setFont(ff); p.setPen(mu if done else fg)
                p.save(); p.setClipRect(tr); p.drawText(tr, s.WR, x["name"] or "—"); p.restore()
                if x["pin"]: p.setFont(f); p.drawText(QRectF(rc.right() - s.P - 22, y, 22, 22), Qt.AlignmentFlag.AlignCenter, w.pin_e())
                y += th
                # 세부 내용
                if mh:
                    y += 8; mr = QRectF(rc.x() + s.P, y, tw, mh); p.setFont(f); d = s.mdoc(x, int(tw), f)
                    ctx = QAbstractTextDocumentLayout.PaintContext(); pal = QPalette(); pal.setColor(QPalette.ColorRole.Text, mu if done else body)
                    pal.setColor(QPalette.ColorRole.Link, QColor(t["accent"])); ctx.palette = pal; ctx.clip = QRectF(0, 0, tw, mh)
                    p.save(); p.setClipRect(mr); p.translate(mr.topLeft()); d.documentLayout().draw(p, ctx); p.restore(); y += mh
                # 하단 한 줄: [중요도][진행상태][마감일]
                y += 12; p.setFont(fs); cx = rc.x() + s.P; right = rc.right() - s.P
                chips = [(w.lname("prio", x["prio"]), w.lcol("prio", x["prio"])), (w.lname("status", x["status"]), w.lcol("status", x["status"]))]
                if x["due"]: chips.append((x["due"][5:].replace("-", ".") if x["due"][:4] == td[:4] else x["due"].replace("-", "."), None))
                for txt, col in chips:
                    av = right - cx
                    if av < 24: break
                    cwd = min(fms.horizontalAdvance(txt) + 14, av); r2 = QRectF(cx, y, cwd, ch)
                    if col:
                        c = QColor(col); c.setAlpha(130 if done else 255); p.setPen(Qt.PenStyle.NoPen); p.setBrush(c); p.drawRoundedRect(r2, 6, 6); p.setPen(QColor(ontext(col)))
                    else:
                        od = w.overdue(x); p.setPen(QPen(red if od else bd, 1)); p.setBrush(Qt.BrushStyle.NoBrush); p.drawRoundedRect(r2.adjusted(.5, .5, -.5, -.5), 6, 6); p.setPen(red if od else mu)
                    p.drawText(r2, Qt.AlignmentFlag.AlignCenter, fms.elidedText(txt, Qt.TextElideMode.ElideRight, int(cwd - 10))); cx += cwd + 5
        except Exception:
            pass


class FolderPanel(QFrame):
    """왼쪽 폴더 목록. 선택한 폴더의 작업만 모든 뷰에 표시. 더블클릭=이름 변경, 우클릭=메뉴"""
    W = 206
    def __init__(s, w):
        super().__init__(); s.w = w; s.busy = False; s.setObjectName("fp"); s._fw = 0 if w.d["ui"].get("fold") else s.W; s.setFixedWidth(s._fw)
        if not s._fw: s.hide()
        s.inn = QWidget(s); s.inn.setFixedWidth(s.W)
        s.anim = QPropertyAnimation(s, b"fw"); s.anim.setDuration(180); s.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        L = w.L; v = QVBoxLayout(s.inn); v.setContentsMargins(22, 0, 0, 18); v.setSpacing(6)
        lb = QLabel(L["folders"]); lb.setObjectName("mu"); lb.setContentsMargins(6, 0, 0, 0); v.addWidget(lb)
        s.lw = QListWidget(); s.lw.setObjectName("folders"); s.lw.setIconSize(QSize(18, 18)); s.lw.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        s.lw.customContextMenuRequested.connect(s.menu); s.lw.currentItemChanged.connect(s.chg); s.lw.itemChanged.connect(s.ren); v.addWidget(s.lw, 1)
        ab = QPushButton("+  " + L["newf"]); ab.setObjectName("cell"); ab.clicked.connect(lambda: w.add_folder()); v.addWidget(ab)
        # 휴지통 (사이드바 최하단). 우클릭 = 아이콘 변경 / 휴지통 비우기
        v.addSpacing(4); v.addWidget(hr()); v.addSpacing(2)
        s.tw = QListWidget(); s.tw.setObjectName("folders"); s.tw.setIconSize(QSize(18, 18)); s.tw.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        s.tw.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff); s.tw.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        s.tw.customContextMenuRequested.connect(s.tmenu); s.tw.currentItemChanged.connect(s.tchg); v.addWidget(s.tw)
    # ----- 접기/펼치기 (fw = 현재 패널 너비)
    def _get(s): return s._fw
    def _set(s, v): s._fw = int(v); s.setFixedWidth(s._fw); s.setVisible(s._fw > 0)
    fw = pyqtProperty(int, _get, _set)
    def resizeEvent(s, e): super().resizeEvent(e); s.inn.setGeometry(0, 0, s.W, s.height())
    def slide(s, show): s.anim.stop(); s.anim.setStartValue(s._fw); s.anim.setEndValue(s.W if show else 0); s.anim.start()
    def reload(s, edit=None):
        w = s.w; s.busy = True; s.lw.clear(); cur = w.d["ui"]["folder"]; tg = None
        for fid, name in [("", w.L["allf"])] + [(f["id"], f["name"]) for f in w.d["folders"]]:
            it = QListWidgetItem(w.ficon_of(fid), name); it.setData(Qt.ItemDataRole.UserRole, fid)
            if fid: it.setFlags(it.flags() | Qt.ItemFlag.ItemIsEditable)
            s.lw.addItem(it)
            if fid == cur: tg = it
        tg = tg or s.lw.item(0)
        if cur != TRASH: s.lw.setCurrentItem(tg)
        s.tw.clear(); ti = QListWidgetItem(); ti.setData(Qt.ItemDataRole.UserRole, TRASH); s.tw.addItem(ti); s.upd_trash()
        s.tw.setFixedHeight(max(s.tw.sizeHintForRow(0), s.fontMetrics().height() + 16) + 6)
        s.busy = False; s.sync()
        if edit: QTimer.singleShot(0, lambda: s.lw.editItem(tg))
    def upd_trash(s):
        """휴지통 항목의 아이콘/개수 표시만 갱신"""
        it = s.tw.item(0)
        if not it: return
        n = len(s.w.d["trash"]); it.setIcon(s.w.ticon_of()); it.setText(s.w.L["trash"] + (f"  ({n})" if n else ""))
    def sync(s):
        """현재 폴더(또는 휴지통)에 맞춰 두 목록의 선택 표시를 맞춤"""
        cur = s.w.d["ui"].get("folder", ""); s.busy = True
        if cur == TRASH:
            s.lw.setCurrentRow(-1); s.lw.clearSelection(); s.tw.setCurrentRow(0)
        else:
            s.tw.setCurrentRow(-1); s.tw.clearSelection()
            for i in range(s.lw.count()):
                if s.lw.item(i).data(Qt.ItemDataRole.UserRole) == cur:
                    if s.lw.currentRow() != i: s.lw.setCurrentRow(i)
                    break
        s.busy = False
    def tchg(s, cur, prev):
        if s.busy or cur is None: return
        s.w.set_folder(TRASH)
    def tmenu(s, pos):
        L = s.w.L; m = QMenu(s); c = m.addAction(L["icon"]); e = m.addAction(L["emptyt"]); e.setEnabled(bool(s.w.d["trash"]))
        r = m.exec(s.tw.viewport().mapToGlobal(pos))
        if r is c: s.w.set_ficon(TRASH)
        elif r is e: s.w.empty_trash()
    def chg(s, cur, prev):
        if s.busy or cur is None: return
        s.w.set_folder(cur.data(Qt.ItemDataRole.UserRole))
    def ren(s, it):
        if s.busy: return
        f = next((f for f in s.w.d["folders"] if f["id"] == it.data(Qt.ItemDataRole.UserRole)), None)
        if not f: return
        n = it.text().strip()
        if not n: s.busy = True; it.setText(f["name"]); s.busy = False; return
        f["name"] = n; s.w.save()
        if s.w.side.x: s.w.side.show_(s.w.side.x)
    def menu(s, pos):
        it = s.lw.itemAt(pos)
        if not it: return
        fid = it.data(Qt.ItemDataRole.UserRole); L = s.w.L; m = QMenu(s); a = b = None
        if fid: a = m.addAction(L["rn"])
        c = m.addAction(L["icon"])
        if fid: b = m.addAction(L["delf"])
        r = m.exec(s.lw.viewport().mapToGlobal(pos))
        if r is None: return
        if r is a: s.lw.editItem(it)
        elif r is c: s.w.set_ficon(fid)
        elif r is b: s.w.del_folder(fid)


class Host(QWidget):
    """본문 영역. 사이드바(오버레이)를 창 크기에 맞춰 다시 배치"""
    def resizeEvent(s, e):
        super().resizeEvent(e)
        sd = getattr(s, "side", None)
        if sd: sd.place()


class MdView(QTextBrowser):
    """메모 미리보기(마크다운 렌더링). 체크박스 클릭 = 체크 토글, 더블클릭(빈 메모는 클릭) = 편집으로 전환, 링크 클릭 = 브라우저로 열기"""
    checkClicked = pyqtSignal(int); dbl = pyqtSignal()
    def __init__(s):
        super().__init__(); s.setObjectName("mdv"); s.setOpenLinks(False); s.anchorClicked.connect(QDesktopServices.openUrl); s.setMouseTracking(True)
    def chk_at(s, pos):
        """pos(뷰포트 좌표)가 체크박스 위면 문서 안 체크박스 순번(0부터), 아니면 -1"""
        try:
            NM = QTextBlockFormat.MarkerType.NoMarker; b = s.cursorForPosition(pos).block()
            if not b.isValid() or b.blockFormat().marker() == NM: return -1
            r = s.cursorRect(QTextCursor(b))
            if not (r.left() - 40 <= pos.x() < r.left() + 1 and r.top() - 3 <= pos.y() <= r.bottom() + 3): return -1
            n = 0; bb = s.document().begin()
            while bb.isValid() and bb.blockNumber() < b.blockNumber():
                if bb.blockFormat().marker() != NM: n += 1
                bb = bb.next()
            return n
        except Exception:
            return -1
    def mousePressEvent(s, e):
        if e.button() == Qt.MouseButton.LeftButton:
            if s.document().isEmpty(): s.dbl.emit(); return
            n = s.chk_at(e.position().toPoint())
            if n >= 0: s.checkClicked.emit(n); return
        super().mousePressEvent(e)
    def mouseMoveEvent(s, e):
        super().mouseMoveEvent(e); p = e.position().toPoint()
        s.viewport().setCursor(Qt.CursorShape.PointingHandCursor if (s.chk_at(p) >= 0 or s.anchorAt(p)) else Qt.CursorShape.IBeamCursor)
    def mouseDoubleClickEvent(s, e):
        if e.button() == Qt.MouseButton.LeftButton and s.chk_at(e.position().toPoint()) < 0: s.dbl.emit(); return
        super().mouseDoubleClickEvent(e)


class Side(QFrame):
    W = 340
    def __init__(s, w, host):
        super().__init__(host); s.w = w; s.x = None; s._off = 0; s.setObjectName("side"); s.hide()
        s.anim = QPropertyAnimation(s, b"off"); s.anim.setDuration(180); s.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        L = w.L; v = QVBoxLayout(s); v.setContentsMargins(18, 16, 18, 16); v.setSpacing(10)
        hd = QHBoxLayout(); hd.addWidget(QLabel(L["detail"])); hd.addStretch(); cb = QPushButton("✕"); cb.setObjectName("cell"); cb.clicked.connect(s.dismiss); hd.addWidget(cb); v.addLayout(hd)
        # 1. 제목  2. 메모
        s.name = QLineEdit(); s.name.setObjectName("nm"); s.name.setPlaceholderText(L["ph"]); s.name.textEdited.connect(lambda t: s.edit("name", t)); v.addWidget(s.name)
        # 메모: [편집] 마크다운 원문 / [미리보기] 렌더링  (Ctrl+E 전환, 편집 중 Esc = 미리보기)
        mh = QHBoxLayout(); mh.setSpacing(2); ml = QLabel(L["memo"]); ml.setObjectName("mu"); mh.addWidget(ml); mh.addStretch(); s.mg = QButtonGroup(s); s.mb = []
        for k, n in enumerate((L["medit"], L["mprev"])):
            b = QPushButton(n); b.setObjectName("seg"); b.setCheckable(True); b.setAutoDefault(False); b.setStyleSheet("padding:3px 10px"); s.mg.addButton(b, k); s.mb.append(b); mh.addWidget(b)
        s.mg.idClicked.connect(lambda k: s.mode(k, True)); v.addLayout(mh)
        s.ms = QStackedWidget(); s.ms.setMinimumHeight(120)
        s.memo = QTextEdit(); s.memo.setAcceptRichText(False); s.memo.setPlaceholderText(L["mdhint"]); s.memo.textChanged.connect(lambda: s.edit("memo", s.memo.toPlainText()))
        s.mv = MdView(); s.mv.setPlaceholderText(L["mdempty"]); s.mv.checkClicked.connect(s.chk); s.mv.dbl.connect(lambda: s.mode(0, True))
        s.ms.addWidget(s.memo); s.ms.addWidget(s.mv); v.addWidget(s.ms, 1)
        sc = QShortcut(QKeySequence("Ctrl+E"), s, activated=lambda: s.mode(1 - s.ms.currentIndex(), True)); sc.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        ec = QShortcut(QKeySequence("Escape"), s.memo, activated=lambda: s.mode(1)); ec.setContext(Qt.ShortcutContext.WidgetShortcut)
        v.addWidget(hr())
        # 하단 속성: 우선순위 / 상태 / 마감일 / 시작일 / 종료일 / 태그
        f = QFormLayout(); f.setContentsMargins(0, 0, 0, 0); f.setHorizontalSpacing(14); f.setVerticalSpacing(8)
        f.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter); f.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        s.cb = {}
        for k, n in (("prio", L["cols"][1]), ("status", L["cols"][2])):
            c = QComboBox(); c.activated.connect(lambda i, k=k: s.x and w.setf(s.x, k, s.cb[k].itemData(i))); s.cb[k] = c; f.addRow(n, c)
        s.db = {}
        for k in ("due", "start", "end"):
            b = QPushButton(); b.setStyleSheet("text-align:left;padding:5px 8px"); b.clicked.connect(lambda _, k=k: w.pick(s.x, k)); s.db[k] = b; f.addRow(L[k], b)
        s.tags = QLineEdit(); s.tags.setPlaceholderText(L["tags"]); s.tags.textEdited.connect(lambda t: s.edit("tags", t)); f.addRow(L["cols"][5], s.tags)
        s.fcb = QComboBox(); s.fcb.activated.connect(lambda i: w.setfolder(s.x, s.fcb.itemData(i))); f.addRow(L["folder"], s.fcb)
        s.colb = QPushButton(); s.colb.setAutoDefault(False); s.colb.clicked.connect(s.colmenu); f.addRow(L["rcol"], s.colb)
        v.addLayout(f)
        d = QPushButton(L["del1"]); d.setObjectName("danger"); d.clicked.connect(lambda: w.delete([s.x["id"]])); v.addWidget(d)
    # ----- 오버레이 위치/애니메이션 (off = 화면에 드러난 너비)
    def _get(s): return s._off
    def _set(s, v): s._off = int(v); s.place()
    off = pyqtProperty(int, _get, _set)
    def place(s):
        h = s.parentWidget()
        if h is None: return
        s.setGeometry(h.width() - s._off, 0, s.W, h.height()); s.setVisible(s._off > 0)
    def edit(s, k, v):
        if not s.x: return
        s.x[k] = [a.strip() for a in v.split(",") if a.strip()] if k == "tags" else v; s.w.save(); s.w.refresh(True)
    def colmenu(s):
        if not s.x: return
        m = QMenu(s); s.w.fill_color_menu(m, [s.x["id"]]); m.exec(s.colb.mapToGlobal(QPoint(0, s.colb.height())))
    def mode(s, m, focus=False):
        """메모 0=편집 / 1=미리보기"""
        if m == 1: s.render()
        s.ms.setCurrentIndex(m); s.mb[m].setChecked(True)
        if focus and m == 0:
            s.memo.setFocus(); c = s.memo.textCursor(); c.movePosition(QTextCursor.MoveOperation.End); s.memo.setTextCursor(c)
    def render(s):
        sb = s.mv.verticalScrollBar(); y = sb.value(); md_render(s.mv.document(), s.memo.toPlainText(), s.w.d["theme"]); sb.setValue(y)
    def chk(s, n):
        """미리보기에서 n번째 체크박스 클릭 → 원문의 [ ] / [x] 토글 후 저장"""
        if not s.x: return
        new = toggle_chk(s.x["memo"], n)
        if new != s.x["memo"]: s.memo.setPlainText(new); s.render()
    def show_(s, x):
        same = s.x is x; s.x = None; s.name.setText(x["name"]); s.tags.setText(", ".join(x["tags"]))
        if s.memo.toPlainText() != x["memo"]: s.memo.setPlainText(x["memo"])
        for k, c in s.cb.items():
            c.clear()
            for l in s.w.LB(k): c.addItem(sw(l["color"]), s.w.lname(k, l["id"]), l["id"])
            c.setCurrentIndex(max(c.findData(x[k]), 0))
        cc = x.get("color") or ""; s.colb.setText(cc or s.w.L["rcnone"])
        s.colb.setStyleSheet(f"background:{cc};color:{ontext(cc)};border:0;text-align:left;padding:5px 8px" if cc else "text-align:left;padding:5px 8px")
        for k, b in s.db.items():
            b.setText(x[k] or s.w.L["none"])
            b.setStyleSheet("text-align:left;padding:5px 8px" + (";color:#ef4444;font-weight:600" if k == "due" and s.w.overdue(x) else ""))
        s.fcb.clear(); s.fcb.addItem(s.w.L["none"], "")
        for f in s.w.d["folders"]: s.fcb.addItem(s.w.ficon_of(f["id"]), f["name"], f["id"])
        s.fcb.setCurrentIndex(max(s.fcb.findData(x.get("folder", "")), 0)); s.x = x; s.raise_()
        s.mode(s.ms.currentIndex() if same else (1 if x["memo"].strip() else 0))
        if s._off < s.W: s.anim.stop(); s.anim.setStartValue(s._off); s.anim.setEndValue(s.W); s.anim.start()
    def close_(s): s.x = None; s.anim.stop(); s.anim.setStartValue(s._off); s.anim.setEndValue(0); s.anim.start()
    def dismiss(s): s.w.tb.clearSelection(); s.close_()


class ColHeader(QHeaderView):
    """열 머리글: 경계선에 마우스를 올리면 ↔ 커서, 끌면 열 너비 조절 / 우클릭 = 기본 너비로 되돌리기
    - st(늘어나는 열)는 남는 공간을 채우므로, 경계를 끌면 그 양옆 두 열 너비가 함께 바뀌어 경계선이 마우스를 그대로 따라감
    - 너비는 w.d["ui"][key] 에 {"열번호": 너비} 로 저장
    - free=True(작업 표): 엑셀처럼 경계선 왼쪽 열 하나만 너비가 바뀌고(늘어나는 열 없음), 열 합계가 화면보다 넓어지면 가로 스크롤
      맨 오른쪽 열의 오른쪽 경계선도 끌 수 있음. 표 오른쪽에는 여백(TaskTable.PAD)이 있어 계속 넓힐 수 있음"""
    GRIP = 5   # 경계선 좌우로 잡을 수 있는 범위(px)
    def __init__(s, w, key, dflt, st, mins=None, flt=False, free=False):
        super().__init__(Qt.Orientation.Horizontal); s.w = w; s.key = key; s.dflt = dict(dflt); s.st = st; s.mins = mins or {}; s.rz = None; s.flt = flt; s.free = free   # flt: 필터 아이콘(깔때기) 표시
        if free: s.setStretchLastSection(False)
        s.setSectionsClickable(True); s.setHighlightSections(True); s.setMouseTracking(True); s.viewport().setMouseTracking(True)
    def mn(s, c): return s.mins.get(c, 120 if c == s.st else 56)
    def widths(s):
        u = s.w.d["ui"].get(s.key); u = u if isinstance(u, dict) else {}; o = {}
        for c, d in s.dflt.items():
            try: v = int(u.get(str(c), d))
            except Exception: v = d
            o[c] = max(s.mn(c), min(4000, v))
        return o
    def apply_widths(s):
        """저장된(없으면 기본) 너비 적용. st 열은 Stretch, 나머지는 Fixed(직접 조절) / free 모드는 모든 열 Fixed"""
        if not s.free: s.setSectionResizeMode(s.st, QHeaderView.ResizeMode.Stretch)
        for c, wd in s.widths().items(): s.setSectionResizeMode(c, QHeaderView.ResizeMode.Fixed); s.resizeSection(c, wd)
    def store(s): s.w.d["ui"][s.key] = {str(c): s.sectionSize(c) for c in s.dflt}; s.w.save()
    def reset_cols(s, cols):
        """주의: reset()은 Qt가 모델 초기화 때 인자 없이 부르는 내장 메서드라 이름을 겹치면 안 됨"""
        for c in cols:
            if c in s.dflt: s.resizeSection(c, s.dflt[c])
        s.store()
    def edge(s, x):
        """x 근처 경계선 → (왼쪽 열, 오른쪽 열). 표의 맨 왼쪽 끝은 제외, 맨 오른쪽 끝은 free 모드에서만 (오른쪽 열 = None)"""
        n = s.count()
        for c in range(n if s.free else n - 1):
            if abs(x - (s.sectionViewportPosition(c) + s.sectionSize(c))) <= s.GRIP: return c, (c + 1 if c + 1 < n else None)
        return None
    def fz(s, c):
        """c열 머리글 오른쪽의 필터 아이콘 클릭 영역 (x 시작, x 끝)"""
        r = s.sectionViewportPosition(c) + s.sectionSize(c) - 1; return r - s.GRIP - 19, r - s.GRIP - 1
    def in_fz(s, x):
        if not s.flt: return -1
        c = s.logicalIndexAt(int(x))
        if c < 0: return -1
        a, b = s.fz(c); return c if a <= x < b else -1
    def paintSection(s, p, rect, c):
        p.save(); super().paintSection(p, rect, c); p.restore()
        if not s.flt or not rect.isValid(): return
        try:
            th = s.w.d["theme"]; ac = QColor(th["accent"]); mu = QColor(mix(th["fg"], th["bg"], .45))
            p.save(); p.setRenderHint(QPainter.RenderHint.Antialiasing); x = rect.right() - s.GRIP - 16; y = rect.center().y() - 5.5
            fun = QPolygonF([QPointF(x, y), QPointF(x + 11, y), QPointF(x + 6.8, y + 5.2), QPointF(x + 6.8, y + 11), QPointF(x + 4.2, y + 9.6), QPointF(x + 4.2, y + 5.2)])
            if s.w.flt_on(c): p.setPen(QPen(ac, 1)); p.setBrush(ac)
            else: p.setPen(QPen(mu, 1.2)); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPolygon(fun)
            k, d = s.w.d["ui"]["sort"]
            if k in s.w.COLS and (7 if c == 0 else c) == k:   # 정렬 중인 열: ▲(오름차순) / ▼(내림차순)
                ax = x - 13; ay = rect.center().y(); p.setPen(Qt.PenStyle.NoPen); p.setBrush(ac)
                tri = [QPointF(ax, ay + 3), QPointF(ax + 8, ay + 3), QPointF(ax + 4, ay - 3)] if d > 0 else [QPointF(ax, ay - 3), QPointF(ax + 8, ay - 3), QPointF(ax + 4, ay + 3)]
                p.drawPolygon(QPolygonF(tri))
            p.restore()
        except Exception:
            pass
    def grab(s, e):
        g = s.edge(int(e.position().x()))
        if not g: return False
        a, b = g; s.rz = dict(a=a, b=b, x=e.position().x(), wa=s.sectionSize(a), wb=s.sectionSize(b) if b is not None else 0); s.viewport().setCursor(Qt.CursorShape.SplitHCursor); return True
    # ----- 마우스
    def mousePressEvent(s, e):
        if e.button() == Qt.MouseButton.LeftButton:
            if s.grab(e): return
            c = s.in_fz(e.position().x())
            if c >= 0:   # 깔때기 아이콘 클릭 = 필터 메뉴 (정렬하지 않음)
                a, _ = s.fz(c); gp = s.mapToGlobal(QPoint(int(a), s.height())); QTimer.singleShot(0, lambda: s.w.flt_menu(c, gp)); return
        super().mousePressEvent(e)
    def mouseDoubleClickEvent(s, e):
        if e.button() == Qt.MouseButton.LeftButton and (s.grab(e) or s.in_fz(e.position().x()) >= 0): return   # 경계선/필터 아이콘 더블클릭이 정렬 클릭으로 처리되지 않도록
        super().mouseDoubleClickEvent(e)
    def mouseMoveEvent(s, e):
        x = e.position().x(); z = s.rz
        if z:
            dx = int(round(x - z["x"]))
            if s.free:   # 엑셀식: 왼쪽 열만 바뀜 → 합계가 화면보다 넓어질 수 있음
                s.resizeSection(z["a"], max(s.mn(z["a"]), min(4000, z["wa"] + dx))); return
            lo = min(0, s.mn(z["a"]) - z["wa"]); hi = max(0, z["wb"] - s.mn(z["b"])); dx = max(lo, min(hi, dx))
            if z["a"] != s.st: s.resizeSection(z["a"], z["wa"] + dx)
            if z["b"] != s.st: s.resizeSection(z["b"], z["wb"] - dx)
            return
        if e.buttons() == Qt.MouseButton.NoButton:
            if s.edge(int(x)): s.viewport().setCursor(Qt.CursorShape.SplitHCursor)
            elif s.in_fz(x) >= 0: s.viewport().setCursor(Qt.CursorShape.PointingHandCursor)
            else: s.viewport().unsetCursor()
        super().mouseMoveEvent(e)
    def mouseReleaseEvent(s, e):
        if s.rz is not None and e.button() == Qt.MouseButton.LeftButton:
            s.rz = None; s.store()
            if not s.edge(int(e.position().x())): s.viewport().unsetCursor()
            return
        super().mouseReleaseEvent(e)
    def leaveEvent(s, e):
        if s.rz is None: s.viewport().unsetCursor()
        super().leaveEvent(e)
    def contextMenuEvent(s, e):
        """우클릭: 경계선 위 = 양옆 열, 머리글 칸 위 = 그 열 / 또는 모든 열 기본 너비로"""
        L = s.w.L; x = e.pos().x(); g = s.edge(x)
        cols = [c for c in (g if g else (s.logicalIndexAt(x),)) if c in s.dflt]
        m = QMenu(s); a1 = m.addAction(L["colw1"]); a1.setEnabled(bool(cols)); a2 = m.addAction(L["colwall"]); col = s.logicalIndexAt(x); af = al = fc = fa = None
        if s.flt and col >= 0:
            m.addSeparator(); af = m.addAction(L["fltdo"])
            if col in (2, 3): al = m.addAction(L["lbedit"])
            if s.w.flt_on(col): fc = m.addAction(L["fclr"])
            if s.w.d["ui"].get("flt"): fa = m.addAction(L["fall0"])
        r = m.exec(e.globalPos())
        if r is None: pass
        elif r is a1: s.reset_cols(cols)
        elif r is a2: s.reset_cols(list(s.dflt))
        elif r is af: s.w.flt_menu(col, e.globalPos())
        elif r is not None and r is fc: s.w.set_flt(col, None)
        elif r is not None and r is fa: s.w.clear_flt()
        elif r is al: s.w.edit_labels("prio" if col == 2 else "status")
        e.accept()


class TrashTable(QTableWidget):
    """휴지통 표: Delete = 영구 삭제"""
    def __init__(s, tv): super().__init__(0, 5); s.tv = tv
    def keyPressEvent(s, e):
        if e.key() == Qt.Key.Key_Delete: s.tv.w.purge(s.tv.sel()); return
        super().keyPressEvent(e)


class TrashView(QWidget):
    """휴지통 화면. 복구하면 원래 폴더(폴더가 지워졌으면 '전체')의 원래 자리로 돌아감. 더블클릭 = 복구"""
    def __init__(s, w):
        super().__init__(); s.w = w; L = w.L; v = QVBoxLayout(s); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(10)
        hd = QHBoxLayout(); hd.setSpacing(8); tl = QLabel(L["trash"]); tl.setObjectName("title"); hd.addWidget(tl); s.cnt = QLabel(); s.cnt.setObjectName("mu"); hd.addWidget(s.cnt); hd.addStretch()
        s.br = QPushButton(L["restore"]); s.br.setObjectName("primary"); s.br.clicked.connect(lambda: w.restore(s.sel()))
        s.bp = QPushButton(L["purge"]); s.bp.setObjectName("danger"); s.bp.clicked.connect(lambda: w.purge(s.sel()))
        s.be = QPushButton(L["emptyt"]); s.be.setObjectName("danger"); s.be.clicked.connect(lambda: w.empty_trash())
        for b in (s.br, s.bp, s.be): hd.addWidget(b)
        v.addLayout(hd)
        t = s.tb = TrashTable(s); t.setHorizontalHeaderLabels([L["cols"][0], L["ofolder"], L["cols"][1], L["cols"][2], L["dtime"]]); t.verticalHeader().hide(); t.verticalHeader().setDefaultSectionSize(42)
        t.setShowGrid(False); t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows); t.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers); t.setIconSize(QSize(18, 18)); t.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        h = ColHeader(w, "tcolw", {1: 180, 2: 120, 3: 120, 4: 160}, 0); t.setHorizontalHeader(h); h.apply_widths()   # 경계선 드래그로 너비 조절, 우클릭 = 초기화
        t.itemSelectionChanged.connect(s.upd); t.itemDoubleClicked.connect(lambda it: w.restore([it.data(Qt.ItemDataRole.UserRole)]))
        t.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu); t.customContextMenuRequested.connect(s.menu)
        s.emp = QLabel(); s.emp.setObjectName("mu"); s.emp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(t, 1); v.addWidget(s.emp, 1)
    def sel(s):
        t = s.tb; return [t.item(r, 0).data(Qt.ItemDataRole.UserRole) for r in sorted({i.row() for i in t.selectionModel().selectedRows()}) if t.item(r, 0)]
    def fill(s):
        w = s.w; L = w.L; th = w.d["theme"]; t = s.tb; prev = set(s.sel()); xs = w.trash_vis(); fn = {f["id"]: f["name"] for f in w.d["folders"]}
        t.blockSignals(True); t.clearSelection(); t.setRowCount(len(xs))
        for r, x in enumerate(xs):
            fid = x.get("folder", "") if x.get("folder", "") in fn else ""
            try: dt = time.strftime("%Y-%m-%d %H:%M", time.localtime(x.get("deleted_at") or 0))
            except Exception: dt = L["none"]
            cells = ((x["name"] or L["none"], None), (fn.get(fid, L["allf"]), w.ficon_of(fid)), (w.lname("prio", x["prio"]), w.lcol("prio", x["prio"])), (w.lname("status", x["status"]), w.lcol("status", x["status"])), (dt, None))
            for c, (txt, ex) in enumerate(cells):
                it = QTableWidgetItem(txt); it.setData(Qt.ItemDataRole.UserRole, x["id"])
                if isinstance(ex, QIcon): it.setIcon(ex)
                elif ex: it.setForeground(QColor(ex))
                if c == 0 and x["memo"].strip(): it.setToolTip(x["memo"].strip()[:500])
                t.setItem(r, c, it)
            if x["id"] in prev: t.selectionModel().select(t.model().index(r, 0), QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)
        t.blockSignals(False); n = len(w.d["trash"]); s.cnt.setText(L["nsel"].format(n=n) if n else "")
        s.emp.setText(L["empty2"] if n else L["tempty"]); s.emp.setVisible(not xs); t.setVisible(bool(xs)); s.upd()
    def upd(s):
        on = bool(s.sel()); s.br.setEnabled(on); s.bp.setEnabled(on); s.be.setEnabled(bool(s.w.d["trash"]))
    def menu(s, pos):
        if not s.sel(): return
        L = s.w.L; m = QMenu(s); a = m.addAction(L["restore"]); b = m.addAction(L["purge"]); r = m.exec(s.tb.viewport().mapToGlobal(pos))
        if r is a: s.w.restore(s.sel())
        elif r is b: s.w.purge(s.sel())


class ColorBtn(QPushButton):
    def __init__(s, c): super().__init__(); s.c = c; s.pa(); s.clicked.connect(s.pk)
    def pa(s): s.setText(s.c); s.setStyleSheet(f"background:{s.c};color:{ontext(s.c)};border:0")
    def pk(s):
        c = QColorDialog.getColor(QColor(s.c), s)
        if c.isValid(): s.c = c.name(); s.pa()


class LabelDlg(QDialog):
    """우선순위/상태 레이블 편집: 추가·삭제·이름·색 / ▲▼ = 중요도(정렬) 순서 / 새 작업 기본값 / (상태) 완료로 취급"""
    def __init__(s, w, kind, parent=None):
        super().__init__(parent or w); s.w = w; s.k = kind; L = w.L; s.setWindowTitle(L["lbp" if kind == "prio" else "lbs"]); s.setMinimumSize(600, 420)
        cur = w.d["labels"][kind]; s.dflt = cur["default"]; s.rg = None
        s.items = [dict(id=l["id"], name=w.lname(kind, l["id"]), color=l["color"], done=bool(l.get("done"))) for l in cur["items"]]
        v = QVBoxLayout(s); hint = QLabel(L["lbhp" if kind == "prio" else "lbhs"]); hint.setObjectName("mu"); hint.setWordWrap(True); v.addWidget(hint)
        bw = QWidget(); s.box = QVBoxLayout(bw); s.box.setContentsMargins(0, 0, 6, 0); s.box.setSpacing(6)
        sa = QScrollArea(); sa.setWidgetResizable(True); sa.setWidget(bw); v.addWidget(sa, 1)
        ab = QPushButton("+  " + L["lbadd"]); ab.setObjectName("cell"); ab.setAutoDefault(False); ab.clicked.connect(s.add); v.addWidget(ab)
        h = QHBoxLayout(); h.addStretch(); cc = QPushButton(L["cancel"]); cc.setAutoDefault(False); cc.clicked.connect(s.reject)
        ok = QPushButton(L["apply"]); ok.setObjectName("primary"); ok.setAutoDefault(False); ok.clicked.connect(s.ok); h.addWidget(cc); h.addWidget(ok); v.addLayout(h)
        s.build()
    def build(s, focus=None):
        while s.box.count():
            it = s.box.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        if s.rg: s.rg.deleteLater()
        s.rg = QButtonGroup(s); L = s.w.L; n = len(s.items); fe = None
        for k, it in enumerate(s.items):
            row = QWidget(); h = QHBoxLayout(row); h.setContentsMargins(0, 0, 0, 0); h.setSpacing(6)
            num = QLabel(str(k + 1)); num.setObjectName("mu"); num.setFixedWidth(22); h.addWidget(num)
            for tx, d, en in (("▲", -1, k > 0), ("▼", 1, k < n - 1)):
                b = QPushButton(tx); b.setFixedWidth(34); b.setAutoDefault(False); b.setEnabled(en); b.clicked.connect(lambda _=False, k=k, d=d: s.mv(k, d)); h.addWidget(b)
            ed = QLineEdit(it["name"]); ed.setMaxLength(40); ed.textChanged.connect(lambda t, it=it: it.__setitem__("name", t)); h.addWidget(ed, 1)
            if it["id"] == focus: fe = ed
            cb = ColorBtn(it["color"]); cb.setFixedWidth(92); cb.setAutoDefault(False); cb.clicked.connect(lambda _=False, it=it, cb=cb: it.__setitem__("color", cb.c)); h.addWidget(cb)
            if s.k == "status":
                dc = QCheckBox(L["lbdone"]); dc.setChecked(it["done"]); dc.toggled.connect(lambda v, it=it: it.__setitem__("done", bool(v))); h.addWidget(dc)
            rb = QRadioButton(L["lbdef"]); rb.setChecked(it["id"] == s.dflt); s.rg.addButton(rb); rb.toggled.connect(lambda v, it=it: v and setattr(s, "dflt", it["id"])); h.addWidget(rb)
            de = QPushButton("✕"); de.setObjectName("danger"); de.setFixedWidth(34); de.setAutoDefault(False); de.setEnabled(n > 1); de.clicked.connect(lambda _=False, k=k: s.rm(k)); h.addWidget(de)
            s.box.addWidget(row)
        s.box.addStretch()
        if fe: QTimer.singleShot(0, lambda: (fe.setFocus(), fe.selectAll()))
    def mv(s, k, d):
        j = k + d
        if 0 <= j < len(s.items): s.items[k], s.items[j] = s.items[j], s.items[k]; s.build()
    def add(s):
        used = {it["id"] for it in s.items}; i = "l" + uuid.uuid4().hex[:7]
        while i in used: i = "l" + uuid.uuid4().hex[:7]
        s.items.append(dict(id=i, name=f'{s.w.L["lbnew"]} {len(s.items) + 1}', color=PAL[len(s.items) % len(PAL)], done=False)); s.build(focus=i)
    def rm(s, k):
        if len(s.items) <= 1: return
        it = s.items.pop(k)
        if s.dflt == it["id"]: s.dflt = s.items[0]["id"]
        s.build()
    def ok(s):
        if s.w.apply_labels(s.k, s.items, s.dflt, s): s.accept()


class FontPicker(QWidget):
    """설정 창 글꼴 선택: 이름 일부를 입력해 검색(대소문자 무시, 중간 일치) + ▾ 버튼으로 전체 목록 드롭다운"""
    def __init__(s, cur, L):
        super().__init__(); h = QHBoxLayout(s); h.setContentsMargins(0, 0, 0, 0); h.setSpacing(4)
        s.cb = cb = QFontComboBox(); cb.setEditable(True); cb.setInsertPolicy(QComboBox.InsertPolicy.NoInsert); cb.setMaxVisibleItems(15)
        cb.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon); cb.setMinimumContentsLength(16)
        cb.setCurrentFont(QFont(cur)); s.last = cb.currentText()
        # 검색용 자동완성: 이름 중간에 들어간 글자로도 찾기 (예: "gothic" → "Malgun Gothic")
        cp = QCompleter(cb.model(), cb); cp.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive); cp.setFilterMode(Qt.MatchFlag.MatchContains)
        cp.setCompletionMode(QCompleter.CompletionMode.PopupCompletion); cp.setMaxVisibleItems(12); cp.popup().setObjectName("fontpop"); cb.setCompleter(cp)
        cp.activated.connect(s.pick); cb.textActivated.connect(s.pick)
        le = cb.lineEdit(); le.setPlaceholderText(L["fsearch"]); le.setClearButtonEnabled(True); le.editingFinished.connect(lambda: s.pick(le.text())); le.installEventFilter(s)
        b = QPushButton("▾"); b.setFixedWidth(36); b.setAutoDefault(False); b.setToolTip(L["fall"]); b.clicked.connect(cb.showPopup)
        h.addWidget(cb, 1); h.addWidget(b)
    def match(s, t):
        """정확히 일치 → 앞부분 일치 → 중간 일치 순으로 설치된 글꼴 이름 찾기"""
        t = t.strip().lower()
        if not t: return None
        fams = [s.cb.itemText(i) for i in range(s.cb.count())]
        for ok in (lambda f: f.lower() == t, lambda f: f.lower().startswith(t), lambda f: t in f.lower()):
            for f in fams:
                if ok(f): return f
        return None
    def pick(s, t):
        """입력한 글자를 실제 글꼴 이름으로 확정. 맞는 글꼴이 없으면 직전 글꼴로 되돌림"""
        f = s.match(t) or s.last; i = s.cb.findText(f)
        if i >= 0 and i != s.cb.currentIndex(): s.cb.setCurrentIndex(i)
        if s.cb.currentText() != f: s.cb.setEditText(f)
        s.last = f
    def eventFilter(s, o, e):
        # 검색창에서 Enter: 설정 창의 다른 버튼이 눌리지 않도록 여기서 처리
        if e.type() == QEvent.Type.KeyPress and e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            s.pick(o.text()); return True
        return False
    def family(s): s.pick(s.cb.currentText()); return s.last


class TaskTable(QTableWidget):
    """작업 테이블: 다중 선택(Shift/Ctrl/드래그) + 드래그로 순서 변경 + 단축키(Delete, Ctrl+C/V, F2)
    - 이미 선택된 행을 잡고 끌거나, 맨 왼쪽 손잡이(⠿) 칸을 잡고 끌면 → 순서 이동
    - 선택되지 않은 행에서 끌면 → 여러 행 범위 선택"""
    PAD = 240   # 마지막 열 오른쪽 여백(px). 이만큼 더 스크롤되므로 맨 오른쪽 열의 경계선을 잡아 계속 넓힐 수 있음
    def __init__(s, w, rows, cols):
        super().__init__(rows, cols); s.w = w; s.dr = None
        s.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel); s.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        s.horizontalScrollBar().setSingleStep(30)
        s.ind = QFrame(s.viewport()); s.ind.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents); s.ind.hide()
        s.ast = QTimer(s); s.ast.setInterval(30); s.ast.timeout.connect(s._auto)
    def rid(s, r):
        it = s.item(r, 1) if r >= 0 else None
        return it.data(Qt.ItemDataRole.UserRole) if it else None
    def is_act(s, r): return 0 <= r < getattr(s.w, "nact", 0) and s.rid(r) is not None
    def updateGeometries(s):
        """기본 가로 스크롤 범위(= 열 너비 합계)에 오른쪽 여백 PAD 를 더함"""
        super().updateGeometries()
        try:
            hb = s.horizontalScrollBar(); vw = s.viewport().width()
            hb.setRange(0, max(0, s.horizontalHeader().length() + s.PAD - vw)); hb.setPageStep(max(vw, 1))
        except Exception:
            pass
    # ----- 마우스: 드래그 이동 / 드래그 선택
    def mousePressEvent(s, e):
        s.dr = None
        if e.button() == Qt.MouseButton.LeftButton and e.modifiers() == Qt.KeyboardModifier.NoModifier:
            p = e.position().toPoint(); r = s.rowAt(p.y())
            if s.is_act(r) and (s.selectionModel().isRowSelected(r, QModelIndex()) or s.columnAt(p.x()) == 0):
                s.dr = dict(p=p, on=False)
        super().mousePressEvent(e)
    def mouseMoveEvent(s, e):
        if s.dr is None: return super().mouseMoveEvent(e)
        p = e.position().toPoint()
        if not s.dr["on"]:
            if (p - s.dr["p"]).manhattanLength() < QApplication.startDragDistance(): return
            s.dr["on"] = True; s.viewport().setCursor(Qt.CursorShape.ClosedHandCursor); s.ast.start()
            s.ind.setStyleSheet(f"background:{s.w.d['theme']['accent']}")
        s.show_ind(p.y())
    def mouseReleaseEvent(s, e):
        dr = s.dr; s.dr = None
        if dr and dr["on"]:
            ids, k = s.sel_rows_ids(), s.drop_at(int(e.position().y())); s.end_drag()
            QTimer.singleShot(0, lambda: s.w.move_tasks(ids, k)); return   # 셀 위젯 이벤트 처리 중 테이블을 다시 그리지 않도록 지연
        super().mouseReleaseEvent(e)
    def mouseDoubleClickEvent(s, e):
        s.dr = None; super().mouseDoubleClickEvent(e)
    def end_drag(s): s.ast.stop(); s.ind.hide(); s.viewport().unsetCursor()
    def drop_at(s, y):
        """마우스 y 위치 → 진행 중 작업 목록에서 끼워 넣을 위치(0..nact)"""
        n = getattr(s.w, "nact", 0); r = s.rowAt(y)
        if r < 0: return 0 if y < 0 or n == 0 or y < s.rowViewportPosition(0) else n
        if r >= n: return n
        return r + (1 if y > s.rowViewportPosition(r) + s.rowHeight(r) / 2 else 0)
    def show_ind(s, y):
        n = getattr(s.w, "nact", 0); k = s.drop_at(y)
        yy = s.rowViewportPosition(k) if k < n else (s.rowViewportPosition(n - 1) + s.rowHeight(n - 1) if n else 0)
        s.ind.setGeometry(0, max(0, yy - 1), s.viewport().width(), 3); s.ind.show(); s.ind.raise_()
    def _auto(s):
        """드래그 중 위/아래 가장자리에 가까우면 자동 스크롤"""
        if s.dr is None or not s.dr["on"]: return s.end_drag()
        y = s.viewport().mapFromGlobal(QCursor.pos()).y(); h = s.viewport().height(); sb = s.verticalScrollBar()
        if y < 30: sb.setValue(sb.value() - 12)
        elif y > h - 30: sb.setValue(sb.value() + 12)
        s.show_ind(y)
    # ----- 키보드
    def sel_rows_ids(s):
        """선택된 '진행 중' 작업 id (화면 순서)"""
        return [s.rid(r) for r in sorted({i.row() for i in s.selectionModel().selectedRows()}) if s.is_act(r)]
    def keyPressEvent(s, e):
        if s.dr is not None and e.key() == Qt.Key.Key_Escape:
            s.dr = None; s.end_drag(); return
        if s.state() != QAbstractItemView.State.EditingState:
            if e.key() == Qt.Key.Key_Delete: s.w.del_sel(); return
            if e.matches(QKeySequence.StandardKey.Copy): s.w.copy_tasks(); return
            if e.matches(QKeySequence.StandardKey.Paste): s.w.paste_tasks(); return
            if e.key() == Qt.Key.Key_F2: s.w.rename_sel(); return
        super().keyPressEvent(e)


class ViewportFilter(QObject):
    def __init__(self, win, table):
        super().__init__()
        self.win = win
        self.table = table

    def eventFilter(self, obj, event):
        try:
            if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                pt = event.position().toPoint(); index = self.table.indexAt(pt)
                if not index.isValid() and self.table.rowAt(pt.y()) < 0:
                    self.win.add()
                    return True
        except Exception:
            pass
        return super().eventFilter(obj, event)


class Win(QMainWindow):
    # 정렬 키 (w, t). 2/3 = 레이블 편집기의 중요도 순서, 7 = 행 색상(팔레트 순서 → 그 밖의 색은 색상환 순 → 색 없음)
    COLS = {1: lambda w, t: nat(t["name"]), 2: lambda w, t: w.lrank("prio", t["prio"]), 3: lambda w, t: w.lrank("status", t["status"]), 4: lambda w, t: (t["due"] == "", t["due"]),
            5: lambda w, t: (t["start"] == "", t["start"]), 6: lambda w, t: nat(",".join(t["tags"])), 7: lambda w, t: w.ckey(t)}
    def __init__(s):
        super().__init__(); s.d = dict(tasks=[], folders=[], trash=[], lang="ko", theme=json.loads(json.dumps(DT)), ui=dict(sort=[0, 1], tab=0, size=[1280, 760], folder="", fold=False, tagf=[], tagand=False, allicon="", trashicon="", rowh=DEFROWH, flt={}), labels=norm_labels(None, DT)); s.dsel = set(); s.loading = False; s.q = ""; s.cal = date.today().replace(day=1)
        s.keep = set(); s.rowtint = {}; s._rhb = False   # keep: 방금 추가/붙여넣은 작업(열 필터에 가려지지 않게) / rowtint: 행 → 색 / _rhb: 행 높이 동기화 중
        s._rhs = QTimer(s); s._rhs.setSingleShot(True); s._rhs.setInterval(400); s._rhs.timeout.connect(s.save)   # 행 높이 드래그 후 저장 (지연)
        s.P = load_paths(); js = read_json(s.P["settings"]) or {}
        jd = js if same_path(s.P["settings"], s.P["data"]) else (read_json(s.P["data"]) or {})
        s.load_set(js); s.load_data(jd); s.fixup()
        s.resize(*s.d["ui"]["size"]); s.setWindowTitle("Do.Nut"); s.build()
        s._today = date.today(); s._dayt = QTimer(s); s._dayt.setInterval(30000); s._dayt.timeout.connect(s._daycheck); s._dayt.start()   # 날짜 변경 감시 (30초)
    def _daycheck(s):
        """시스템 날짜가 바뀌면(자정 경과·PC 날짜 변경) 기한 초과 표시와 오늘 표시를 다시 그림"""
        if date.today() != s._today:
            s._today = date.today()
            try: s.refresh()
            except Exception: pass
    # ----- 공통
    def save(s, strict=False):
        """설정(lang/theme/ui)은 설정 파일에, 작업(tasks/folders/trash)은 데이터 파일에 저장. 두 경로가 같으면 한 파일에 함께 저장"""
        st = dict(lang=s.d["lang"], theme=s.d["theme"], ui=s.d["ui"]); dt = dict(tasks=s.d["tasks"], folders=s.d["folders"], trash=s.d["trash"], labels=s.d["labels"])
        try:
            if same_path(s.P["settings"], s.P["data"]): write_json(s.P["data"], dict(st, **dt))
            else: write_json(s.P["settings"], st); write_json(s.P["data"], dt)
        except Exception:
            if strict: raise
    def load_set(s, j):
        j = j if isinstance(j, dict) else {}
        if j.get("lang") in TR: s.d["lang"] = j["lang"]
        th = clean_theme(j.get("theme"))
        if th: s.d["theme"] = dict(json.loads(json.dumps(DT)), **th)
        if isinstance(j.get("ui"), dict): s.d["ui"].update(j["ui"])
    def load_data(s, j):
        j = j if isinstance(j, dict) else {}; used = set(); nm = TR.get(s.d["lang"], TR["ko"])["newf"]
        s.d["tasks"] = [x for x in (norm_task(t, used) for t in (j.get("tasks") if isinstance(j.get("tasks"), list) else [])) if x]
        s.d["folders"] = norm_folders(j.get("folders"), nm)
        s.d["trash"] = [x for x in (norm_trash(t, used) for t in (j.get("trash") if isinstance(j.get("trash"), list) else [])) if x]
        s.d["labels"] = norm_labels(j.get("labels"), s.d["theme"])
        for x in s.d["tasks"] + s.d["trash"]: s.lab_fix(x)
    # ----- 레이블 (우선순위 / 상태)
    def LB(s, k): return s.d["labels"][k]["items"]
    def ldef(s, k): return s.d["labels"][k]["default"]
    def lab(s, k, i): return next((l for l in s.LB(k) if l["id"] == i), None) or s.LB(k)[0]
    def dname(s, k, i):
        """기본 레이블의 언어별 이름"""
        b = BUILTIN[k]; L = getattr(s, "L", None) or TR[s.d["lang"]]
        return L["P" if k == "prio" else "S"][b.index(i)] if i in b else L["none"]
    def lname(s, k, i): l = s.lab(k, i); return l["name"] or s.dname(k, l["id"])
    def lcol(s, k, i): return s.lab(k, i)["color"]
    def tcol(s, x): return x.get("color") or s.lcol("prio", x["prio"])   # 작업 색: 행 색상 우선, 없으면 우선순위 색 (표 외 모든 뷰 공통)
    def lrank(s, k, i): return next((n for n, l in enumerate(s.LB(k)) if l["id"] == i), len(s.LB(k)))
    def is_done(s, x): return bool(s.lab("status", x["status"]).get("done"))
    def lab_fix(s, x):
        """작업의 레이블 id가 없는 레이블을 가리키면 기본값으로"""
        for k in ("prio", "status"):
            if x.get(k) not in {l["id"] for l in s.LB(k)}: x[k] = s.ldef(k)
    def ckey(s, t):
        c = t.get("color") or ""
        if not c: return (2, 0, 0)
        if c in PAL: return (0, PAL.index(c), 0)
        q = QColor(c); return (1, q.hslHue() if q.hslHue() >= 0 else 999, q.lightness())
    def edit_labels(s, k, par=None): LabelDlg(s, k, par).exec()
    def apply_labels(s, k, items, dflt, par=None):
        """레이블 편집 결과 적용. 지운 레이블을 쓰던 작업은 기본값 레이블로, 완료 여부가 바뀐 상태는 done_at 갱신"""
        L = s.L; ids = [it["id"] for it in items]; old = {l["id"] for l in s.LB(k)}; gone = old - set(ids)
        if dflt not in ids: dflt = ids[0]
        new = []
        for it in items:
            nm = it["name"].strip()
            if it["id"] in BUILTIN[k] and nm == s.dname(k, it["id"]): nm = ""   # 기본 이름 그대로면 비워 둠 → 언어를 바꾸면 함께 번역
            elif not nm: nm = L["lbnew"]
            o = dict(id=it["id"], name=nm, color=QColor(it["color"]).name() if QColor(it["color"]).isValid() else "#6b7280")
            if k == "status": o["done"] = bool(it.get("done"))
            new.append(o)
        xs = s.d["tasks"] + s.d["trash"]; hit = [x for x in xs if x[k] in gone]
        if hit:
            dn = next(o for o in new if o["id"] == dflt); dn = dn["name"] or s.dname(k, dn["id"])
            if QMessageBox.question(par or s, "?", L["lbdel"].format(n=len(hit), name=dn)) != QMessageBox.StandardButton.Yes: return False
        s.d["labels"][k] = dict(items=new, default=dflt)
        for x in hit: x[k] = dflt
        if k == "status":
            now = time.time()
            for x in xs:
                if s.is_done(x): x["done_at"] = x.get("done_at") or now
                else: x["done_at"] = 0
        F = s.d["ui"].get("flt") or {}; fk = "2" if k == "prio" else "3"
        if fk in F:
            F[fk] = [v for v in F[fk] if v not in gone]
            if not F[fk]: del F[fk]
        s.save(); s.refresh()
        if s.side.x: s.side.show_(s.side.x)
        return True
    def fixup(s):
        """불러온 ui 값 검증"""
        ui = s.d["ui"]
        if s.d["lang"] not in TR: s.d["lang"] = "ko"
        if ui.get("folder", "") not in {f["id"] for f in s.d["folders"]} and ui.get("folder") != TRASH: ui["folder"] = ""
        tf = ui.get("tagf"); ui["tagf"] = [g for g in tf if isinstance(g, str)] if isinstance(tf, list) else []
        try: ok = 0 <= int(ui.get("tab", 0) or 0) < len(TR[s.d["lang"]]["tabs"])
        except Exception: ok = False
        if not ok: ui["tab"] = 0
        sz = ui.get("size")
        if not (isinstance(sz, list) and len(sz) == 2 and all(isinstance(v, int) and v > 200 for v in sz)): ui["size"] = [1280, 760]
        if not isinstance(ui.get("sort"), list) or len(ui["sort"]) != 2: ui["sort"] = [0, 1]
        for k in ("colw", "tcolw"):
            if k in ui and not isinstance(ui[k], dict): del ui[k]
        try: k0 = int(ui["sort"][0]); d0 = 1 if int(ui["sort"][1]) >= 0 else -1
        except Exception: k0, d0 = 0, 1
        ui["sort"] = [k0 if 0 <= k0 <= 7 else 0, d0]
        try: rh = int(ui.get("rowh", DEFROWH))
        except Exception: rh = DEFROWH
        ui["rowh"] = rh if 22 <= rh <= 300 else DEFROWH
        F = ui.get("flt"); cl = {}
        for k, v in (F.items() if isinstance(F, dict) else []):
            if k == "1":
                if isinstance(v, str) and v.strip(): cl[k] = v.strip()
            elif k in ("0", "2", "3", "4", "5", "6") and isinstance(v, list):
                v = [a for a in v if isinstance(a, str)]
                if v: cl[k] = v
        ui["flt"] = cl
    def pin_e(s): return s.d["theme"].get("pin") or DEFPIN
    def ticon_of(s):
        th = s.d["theme"]; e = s.d["ui"].get("trashicon", "")
        return eicon(e) if e else ticon(mix(th["fg"], th["bg"], .55))
    def closeEvent(s, e): s.d["ui"]["size"] = [s.width(), s.height()]; s.save(); super().closeEvent(e)
    def T(s, i): return next((t for t in s.d["tasks"] if t["id"] == i), None)
    def rng(s, t):
        try:
            a = t.get("start") or t.get("end") or t.get("due")
            b = t.get("end") or t.get("start") or t.get("due")
            return (date.fromisoformat(a), date.fromisoformat(b)) if a else None
        except Exception:
            return None
    def vis(s):
        """현재 폴더 + 태그 필터 + 검색어를 모두 통과한 작업"""
        ui = s.d["ui"]; f = ui.get("folder", ""); tf = set(ui.get("tagf") or []); an = ui.get("tagand"); qs = s.q.lower().split(); out = []
        if f == TRASH: return out
        for t in s.d["tasks"]:
            if f and t.get("folder", "") != f: continue
            if tf:
                tg = set(t["tags"])
                if (not tf <= tg) if an else not (tf & tg): continue
            if qs:
                hay = (t["name"] + "\n" + t["memo"] + "\n" + " ".join(t["tags"])).lower()
                if not all(q in hay for q in qs): continue
            if not s.flt_ok(t): continue
            out.append(t)
        return out
    # ----- 열 필터 (ui["flt"] = {"열번호": 값 목록 / "1": 작업명 검색어}). 같은 열 안 = OR, 열끼리 = AND
    def overdue(s, t):
        """마감일이 시스템(PC) 오늘 날짜보다 이전이고 완료되지 않았으면 True"""
        return bool(t.get("due")) and not s.is_done(t) and s.due_cat(t, date.today()) == "over"
    def due_cat(s, t, td):
        if not t["due"]: return "none"
        try: d = date.fromisoformat(t["due"])
        except Exception: return "none"
        return "over" if d < td else "today" if d == td else "week" if d <= td + timedelta(7) else "later"
    def tl_cat(s, t, td):
        if not (t["start"] or t["end"]): return "none"
        r = s.rng(t)
        if not r: return "none"
        return "past" if r[1] < td else "future" if r[0] > td else "now"
    def flt_ok(s, t):
        F = s.d["ui"].get("flt") or {}
        if not F or t["id"] in s.keep: return True
        td = date.today(); v = F.get("0")
        if v:
            pins = {a for a in v if a in ("pin", "nopin")}; cs = {a for a in v if a.startswith("c:")}
            if pins and ("pin" if t["pin"] else "nopin") not in pins: return False
            if cs and "c:" + (t.get("color") or "") not in cs: return False
        q = F.get("1")
        if q and not all(w in t["name"].lower() for w in q.lower().split()): return False
        for c, k in (("2", "prio"), ("3", "status")):
            if F.get(c) and t[k] not in F[c]: return False
        if F.get("4") and s.due_cat(t, td) not in F["4"]: return False
        if F.get("5") and s.tl_cat(t, td) not in F["5"]: return False
        v = F.get("6")
        if v:
            tg = set(t["tags"])
            if not ((not tg and "" in v) or (tg & set(v))): return False
        return True
    def flt_on(s, c): return bool((s.d["ui"].get("flt") or {}).get(str(c)))
    def flt_opts(s, c):
        """필터 메뉴 항목 (값, 표시 이름, 아이콘). 값 None = 제목(비활성) 또는 구분선(이름 빈칸)"""
        L = s.L; F = s.d["ui"].get("flt") or {}; cur = F.get(str(c), [])
        if c == 0:
            used = sorted({t.get("color") for t in s.d["tasks"] if t.get("color") and t.get("color") not in PAL} | {a[2:] for a in cur if a.startswith("c:#") and a[2:] not in PAL})
            return ([(None, L["fpinh"], None), ("pin", L["fpin"], None), ("nopin", L["fnopin"], None), (None, "", None), (None, L["fcol"], None), ("c:", L["rcnone"], None)]
                    + [("c:" + c2, c2, sw(c2)) for c2 in PAL + used])
        if c in (2, 3):
            k = "prio" if c == 2 else "status"; return [(l["id"], s.lname(k, l["id"]), sw(l["color"])) for l in s.LB(k)]
        if c == 4: return list(zip(("none", "over", "today", "week", "later"), L["dc"], [None] * 5))
        if c == 5: return list(zip(("none", "now", "past", "future"), L["tc"], [None] * 4))
        if c == 6:
            tags = s.all_tags(); return [("", L["fnotag"], None)] + [(g, "# " + g, None) for g in tags + [g for g in cur if g and g not in tags]]
        return []
    def set_flt(s, c, v):
        F = s.d["ui"].setdefault("flt", {})
        if v: F[str(c)] = v
        else: F.pop(str(c), None)
        s.keep.clear(); s.save(); s.refresh()
    def flt_tog(s, c, v, on):
        F = s.d["ui"].get("flt") or {}; s.set_flt(c, [a for a in F.get(str(c), []) if a != v] + ([v] if on else []))
    def clear_flt(s): s.d["ui"]["flt"] = {}; s.keep.clear(); s.save(); s.refresh()
    def set_sort(s, k, d): s.d["ui"]["sort"] = [k, d]; s.save(); s.refresh()
    def clear_sort(s): s.set_sort(0, 1)   # 정렬 해제 = 수동 순서
    def cycle_sort(s, k):
        """같은 열을 반복 선택: 오름차순 → 내림차순 → 해제"""
        ck, cd = s.d["ui"]["sort"]
        if ck != k: s.set_sort(k, 1)
        elif cd > 0: s.set_sort(k, -1)
        else: s.clear_sort()
    def flt_menu(s, c, gp):
        """머리글 깔때기 아이콘 클릭: 정렬 / 값 선택(여러 개, 메뉴가 닫히지 않음) / 해제"""
        if s.d["ui"].get("folder") == TRASH: return
        L = s.L; F = s.d["ui"].get("flt") or {}; m = StayMenu(s); kk = 7 if c == 0 else c; chk = []; le0 = []
        for tx, d in ((L["sasc"], 1), (L["sdesc"], -1)):
            a = m.addAction((L["csort"] + " · " if c == 0 else "") + tx); a.setCheckable(True); a.setChecked(s.d["ui"]["sort"] == [kk, d])
            a.triggered.connect(lambda _=False, d=d: s.set_sort(kk, d))
        a = m.addAction((L["csort"] + " · " if c == 0 else "") + L["sclr"]); a.setEnabled(s.d["ui"]["sort"][0] == kk); a.triggered.connect(lambda _=False: s.clear_sort())
        m.addSeparator()
        if c == 1:
            le = QLineEdit(F.get("1", "")); le.setPlaceholderText(L["ftext"]); le.setClearButtonEnabled(True); le.setMinimumWidth(260); le0.append(le)
            box = QWidget(); bl = QHBoxLayout(box); bl.setContentsMargins(8, 4, 8, 4); bl.addWidget(le); wa = QWidgetAction(m); wa.setDefaultWidget(box); m.addAction(wa)
            tm = QTimer(m); tm.setSingleShot(True); tm.setInterval(250); go = lambda: s.set_flt(1, le.text().strip())
            tm.timeout.connect(go); le.textChanged.connect(lambda _: tm.start()); le.returnPressed.connect(lambda: (tm.stop(), go(), m.close()))
            m.aboutToHide.connect(lambda: tm.isActive() and (tm.stop(), go())); QTimer.singleShot(0, le.setFocus)
        else:
            cur = set(F.get(str(c), []))
            for v, tx, ic in s.flt_opts(c):
                if v is None:
                    if tx: a = m.addAction(tx); a.setEnabled(False)
                    else: m.addSeparator()
                    continue
                a = m.addAction(ic, tx) if ic else m.addAction(tx); a.setCheckable(True); a.setChecked(v in cur); a.toggled.connect(lambda on, v=v: s.flt_tog(c, v, on)); chk.append((v, a))
        m.addSeparator()
        a = m.addAction(L["fclr"]); b = m.addAction(L["fall0"])
        def sync(*_):   # 메뉴가 열려 있는 동안에도 '해제' 항목의 활성 상태·체크 표시를 현재 필터에 맞춤
            FF = s.d["ui"].get("flt") or {}; now = set(FF.get(str(c), []))
            a.setEnabled(bool(FF.get(str(c)))); b.setEnabled(bool(FF))
            for v, x in chk:
                if x.isChecked() != (v in now): x.blockSignals(True); x.setChecked(v in now); x.blockSignals(False)
        def clr_col(*_):
            s.set_flt(c, None)
            if c == 1 and le0: le0[0].blockSignals(True); le0[0].clear(); le0[0].blockSignals(False)
            sync()
        def clr_all(*_):
            s.clear_flt()
            if le0: le0[0].blockSignals(True); le0[0].clear(); le0[0].blockSignals(False)
            sync()
        a.triggered.connect(clr_col); b.triggered.connect(clr_all)
        for _v, x in chk: x.toggled.connect(lambda *_: QTimer.singleShot(0, sync))
        if le0: le0[0].textChanged.connect(lambda *_: QTimer.singleShot(300, sync))
        sync()
        if c in (2, 3):
            m.addSeparator(); e = m.addAction(L["lbedit"]); e.triggered.connect(lambda: QTimer.singleShot(0, lambda: s.edit_labels("prio" if c == 2 else "status")))
        m.exec(gp)
    def ficon_of(s, fid):
        th = s.d["theme"]
        e = next((f.get("icon", "") for f in s.d["folders"] if f["id"] == fid), "") if fid else s.d["ui"].get("allicon", "")
        return eicon(e) if e else ficon(th["accent"] if fid else mix(th["fg"], th["bg"], .55))
    def order(s, L):
        k, d = s.d["ui"]["sort"]
        if k in s.COLS: L = sorted(L, key=lambda t: s.COLS[k](s, t), reverse=d < 0)
        return [t for t in L if t["pin"]] + [t for t in L if not t["pin"]]
    # ----- UI
    def build(s):
        L = s.L = TR[s.d["lang"]]; s.setStyleSheet(qss(s.d["theme"])); cw = QWidget(); s.setCentralWidget(cw); root = QVBoxLayout(cw); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)
        top = QHBoxLayout(); top.setContentsMargins(22, 16, 22, 12); tg = QPushButton("☰"); tg.setObjectName("ico"); tg.setFixedSize(36, 36); tg.setToolTip(L["ftog"]); tg.clicked.connect(lambda: s.toggle_folders()); top.addWidget(tg); top.addSpacing(6)
        lg = QLabel(); lp = QPixmap(); lp.loadFromData(QByteArray.fromBase64(LOGO.encode())); dpr = s.devicePixelRatioF(); lp = lp.scaled(int(26 * dpr), int(26 * dpr), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation); lp.setDevicePixelRatio(dpr)
        lg.setPixmap(lp); lg.setFixedSize(26, 26); top.addWidget(lg); top.addSpacing(8)
        tl = QLabel(L["app"]); tl.setObjectName("title"); top.addWidget(tl); top.addSpacing(20)
        s.grp = QButtonGroup(s)
        for i, n in enumerate(L["tabs"]): b = QPushButton(n); b.setObjectName("seg"); b.setCheckable(True); s.grp.addButton(b, i); top.addWidget(b)
        s.grp.idClicked.connect(s.switch); top.addStretch()
        s.search = QLineEdit(s.q); s.search.setPlaceholderText(L["search"]); s.search.setClearButtonEnabled(True); s.search.setFixedWidth(220); s.search.textChanged.connect(s.set_q); top.addWidget(s.search)
        QShortcut(QKeySequence("Ctrl+F"), cw, activated=lambda: (s.search.setFocus(), s.search.selectAll()))
        es = QShortcut(QKeySequence("Escape"), s.search, activated=s.search.clear); es.setContext(Qt.ShortcutContext.WidgetShortcut)
        s.tbn = QPushButton(); s.tbn.setObjectName("flt"); s.tmenu = StayMenu(s.tbn); s.tbn.setMenu(s.tmenu); s.tmenu.aboutToShow.connect(s.tag_menu); top.addWidget(s.tbn); top.addSpacing(4)
        s.vbn = QPushButton(); s.vbn.setObjectName("flt"); s.vmenu = QMenu(s.vbn); s.vbn.setMenu(s.vmenu); s.vmenu.aboutToShow.connect(s.view_menu); top.addWidget(s.vbn); top.addSpacing(8)
        for txt, fn, ob in ((L["add"], lambda: s.add(), "primary"), ("⚙  " + L["settings"], s.settings, "")):
            b = QPushButton(txt); b.setObjectName(ob); b.clicked.connect(fn); top.addWidget(b)
        root.addLayout(top); mid = QHBoxLayout(); mid.setContentsMargins(0, 0, 0, 0); mid.setSpacing(0); root.addLayout(mid, 1); s.fp = FolderPanel(s); mid.addWidget(s.fp)
        host = Host(); mid.addWidget(host, 1); body = QVBoxLayout(host); body.setContentsMargins(14, 0, 0, 18); body.setSpacing(0)
        s.stack = QStackedWidget(); body.addWidget(s.stack, 1); s.side = host.side = Side(s, host)
        
        t = s.tb = TaskTable(s, 0, 7); t.setHorizontalHeaderLabels([""] + L["cols"]); t.setShowGrid(False); t.setItemDelegate(RowDelegate(s, t))
        # 행 높이: 표 왼쪽 가장자리(세로 머리글)의 행 경계선을 끌어 조절. 여러 행 선택 후 끌면 함께 / 경계선 더블클릭 = 기본 높이
        vh = t.verticalHeader(); vh.setObjectName("rowgrip"); vh.setFixedWidth(12); vh.setMinimumSectionSize(22); vh.setDefaultSectionSize(s.d["ui"]["rowh"]); vh.setToolTip(L["rowhtip"])
        vh.sectionResized.connect(s.on_rowh); vh.sectionHandleDoubleClicked.connect(s.rowh_dbl)
        t.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu); t.customContextMenuRequested.connect(lambda _: s.row_menu())
        t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows); t.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection); t.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.EditKeyPressed)
        h = ColHeader(s, "colw", {0: 84, 1: 360, 2: 112, 3: 112, 4: 128, 5: 106, 6: 116}, 1, {0: 64}, flt=True, free=True); h.setObjectName("fh"); t.setHorizontalHeader(h); h.apply_widths()   # 경계선 드래그로 너비 조절, 우클릭 = 초기화, 깔때기 = 필터
        h.setSortIndicatorShown(False); h.sectionClicked.connect(s.sort_by)   # 정렬 화살표는 ColHeader가 직접 그림
        nd = s.nd = NameDelegate(s, t); nd.ph = L["ph"]; t.setItemDelegateForColumn(1, nd); nd.enter.connect(lambda i: QTimer.singleShot(0, lambda: s.add(i)))
        t.itemChanged.connect(s.item_changed); t.itemSelectionChanged.connect(s.on_sel); t.cellClicked.connect(s.title_click)
        
        s.vp_filter = ViewportFilter(s, t)
        t.viewport().installEventFilter(s.vp_filter)

        s.stack.addWidget(t)
        
        s.gantt = Gantt(s)
        s.cg = CalGrid(s)
        s.tlv = TLView(s)

        s.stack.addWidget(s.gantt.pane())   # index 1 = 간트차트 (이동 막대 + 자체 가로/세로 스크롤바)

        cv = QWidget(); cl = QVBoxLayout(cv); cl.setContentsMargins(0, 0, 0, 0); cl.setSpacing(8)
        nav = QHBoxLayout(); nav.setSpacing(6); s.cl = QLabel(); s.cl.setObjectName("title")
        for tx, dd in (("◀", -1), ("▶", 1)):
            b = QPushButton(tx); b.clicked.connect(lambda _, dd=dd: s.mvcal(dd)); nav.addWidget(b)
        b = QPushButton(L["g_today"]); b.clicked.connect(s.cal_today); nav.addWidget(b)
        nav.addSpacing(6); nav.addWidget(s.cl); nav.addStretch(); cl.addLayout(nav)
        box = QWidget(); g = QHBoxLayout(box); g.setContentsMargins(0, 0, 0, 0); g.setSpacing(0); g.addWidget(s.cg, 1); g.addWidget(s.cg.vb); box.setMinimumSize(7 * 92 + 16, 240)   # 창이 좁으면 하단 가로 스크롤 (세로는 캘린더 자체 스크롤)
        sa = mkscroll(box); sa.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff); cl.addWidget(sa, 1)
        s.stack.addWidget(cv)

        s.stack.addWidget(s.tlv.pane())     # index 3 = 타임라인 (사건 종류 켜기/끄기 + 스크롤)
        s.kv = KeepView(s)
        s.stack.addWidget(mkscroll(s.kv))

        s.tv = TrashView(s); s.stack.addWidget(s.tv)   # index 5 = 휴지통
        
        s.switch(s.d["ui"]["tab"], False)
        s.refresh(); s.fp.reload()
        if s.d["ui"]["tab"] == 3: QTimer.singleShot(150, s.tlv.to_today)
    def switch(s, i, upd=True):
        s.stack.setCurrentIndex(i)
        s.grp.button(i).setChecked(True)
        s.d["ui"]["tab"] = i
        if upd:
            QTimer.singleShot(10, s.views)
            if i == 3: QTimer.singleShot(60, s.tlv.to_today)   # 타임라인은 열 때마다 오늘 기준선으로
    def mvcal(s, n): s.cal = addm(s.cal, n); s.cg.goto(s.cal); s.views()
    def cal_today(s): s.cal = date.today().replace(day=1); s.cg.goto(s.cal); s.views()
    def views(s):
        try:
            if hasattr(s, 'cl') and s.cl:
                s.cl.setText(f"{s.cal.year}.{s.cal.month:02d}")
            if hasattr(s, 'gantt') and s.gantt:
                s.gantt.prep()
            if hasattr(s, 'tlv') and s.tlv:
                s.tlv.prep()
            if hasattr(s, 'cg') and s.cg:
                s.cg.update()
            if hasattr(s, 'kv') and s.kv:
                s.kv.prep()
        except Exception:
            pass
    def sort_by(s, c):
        if c == 0: return
        s.cycle_sort(c)
    def refresh(s, soft=False):
        if soft: return s.views()
        tr = s.d["ui"].get("folder", "") == TRASH
        for b in s.grp.buttons(): b.setEnabled(not tr)
        s.tbn.setEnabled(not tr); s.vbn.setEnabled(not tr)
        if hasattr(s, "tv"):
            if tr: s.stack.setCurrentIndex(5); s.tv.fill()
            elif s.stack.currentIndex() == 5: s.stack.setCurrentIndex(s.d["ui"]["tab"])
        s.fp.upd_trash()
        s.upd_tagbtn(); s.upd_viewbtn(); t = s.tb; s.loading = True; prev = s.sel_ids(); cur = t.rid(t.currentRow())
        t.horizontalHeader().viewport().update()   # 정렬 화살표 / 필터 아이콘 다시 그리기
        t.clearSpans()
        for r in range(t.rowCount()): t.setItemDelegateForRow(r, None)
        vs = s.vis(); t.setRowCount(0); act = s.order([x for x in vs if not s.is_done(x)]); dn = sorted([x for x in vs if s.is_done(x)], key=lambda x: -x.get("done_at", 0))
        t.setRowCount(len(act) + 1 + len(dn)); s.nact = len(act)
        rows = list(enumerate(act)) + [(len(act) + 1 + r, x) for r, x in enumerate(dn)]; th = s.d["theme"]; hv = mix(th["accent"], th["bg"], .35); s.rowtint = {}
        for r, x in rows:
            c = x.get("color")
            if c: s.rowtint[r] = (QColor(mix(c, th["bg"], ROWTINT)), QColor(mix(c, hv, ROWTINT + .1)), QColor(c))
        for r, x in rows: s.fill(r, x)
        s.sep(len(act), dn)
        vh = t.verticalHeader(); dh = s.d["ui"]["rowh"]; vh.setDefaultSectionSize(dh); t.setVerticalHeaderLabels([""] * t.rowCount())
        for r, x in rows: t.setRowHeight(r, max(22, min(300, int(x.get("rowh") or dh))))
        vh.setSectionResizeMode(len(act), QHeaderView.ResizeMode.Fixed)   # 완료함 구분 행은 높이 고정
        for r in range(t.rowCount()):
            it = t.item(r, 1)
            if it and it.data(Qt.ItemDataRole.UserRole) in prev: t.selectionModel().select(t.model().index(r, 0), QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)
            if cur and it and it.data(Qt.ItemDataRole.UserRole) == cur: t.selectionModel().setCurrentIndex(t.model().index(r, 1), QItemSelectionModel.SelectionFlag.NoUpdate)
        s.loading = False; s.views()
    def sel_ids(s):
        """선택된 작업 id (화면 위→아래 순서, 완료함 구분 행 제외)"""
        return [i for i in (s.tb.rid(r) for r in sorted({x.row() for x in s.tb.selectionModel().selectedRows()})) if i]
    def wrap(s, w): c = QWidget(); l = QHBoxLayout(c); l.setContentsMargins(4, 2, 4, 2); l.addWidget(w, 0, Qt.AlignmentFlag.AlignVCenter); return c
    def fill(s, r, x):
        L = s.L; th = s.d["theme"]; t = s.tb; done = s.is_done(x); h = QWidget(); hl = QHBoxLayout(h); hl.setContentsMargins(10, 0, 0, 0)
        if done:
            cb = QCheckBox(); cb.setChecked(x["id"] in s.dsel); cb.toggled.connect(lambda v, i=x["id"]: s.dsel.add(i) if v else s.dsel.discard(i)); hl.addWidget(cb)
        else:
            g = QLabel("⠿"); g.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents); g.setStyleSheet(f"color:{mix(th['fg'], th['bg'], .45)};font-size:16px;background:transparent")
            hl.addWidget(g); h.setCursor(Qt.CursorShape.OpenHandCursor)
        pb = QToolButton(); pb.setCursor(Qt.CursorShape.ArrowCursor); pb.setObjectName("pin"); pb.setFixedSize(30, 30); pb.setText(s.pin_e() if x["pin"] else ""); pb.clicked.connect(lambda _, x=x: (x.__setitem__("pin", not x["pin"]), s.save(), s.refresh())); hl.addWidget(pb); hl.addStretch(); t.setCellWidget(r, 0, h)
        for c, v in ((1, x["name"]), (6, ", ".join(x["tags"]))):
            it = QTableWidgetItem(v); it.setData(Qt.ItemDataRole.UserRole, x["id"])
            if done and c == 1: f = it.font(); f.setStrikeOut(True); it.setFont(f); it.setForeground(QColor(th["fg"]).darker(160))
            t.setItem(r, c, it)
        for c, k in ((2, "prio"), (3, "status")):
            cb = QComboBox()
            for l in s.LB(k): cb.addItem(s.lname(k, l["id"]), l["id"])
            cb.setCurrentIndex(max(cb.findData(x[k]), 0)); cb.setStyleSheet(pill(s.lcol(k, x[k])))
            cb.activated.connect(lambda i, x=x, k=k, cb=cb: s.setf(x, k, cb.itemData(i))); t.setCellWidget(r, c, s.wrap(cb))
        tl = f"{x['start'] or '…'} → {x['end'] or '…'}" if (x["start"] or x["end"]) else L["none"]
        for c, txt, fn in ((4, x["due"] or L["none"], lambda _, x=x: s.pick(x, "due")), (5, tl, lambda _, x=x: s.pickrange(x))):
            b = QPushButton(txt); b.setObjectName("cell"); b.clicked.connect(fn)
            if c == 4 and s.overdue(x): b.setStyleSheet("color:#ef4444;font-weight:600")   # 기한 초과 = 붉은 글씨
            t.setCellWidget(r, c, b)
    def sep(s, r, dn):
        L = s.L; t = s.tb; t.setSpan(r, 0, 1, 7)
        for c in range(7): it = QTableWidgetItem(); it.setFlags(Qt.ItemFlag.NoItemFlags); t.setItem(r, c, it)
        t.setItemDelegateForRow(r, SepDelegate(t, mix(s.d["theme"]["fg"], s.d["theme"]["bg"], .3))); w = QWidget(); l = QHBoxLayout(w); l.setContentsMargins(14, 0, 14, 0)
        b = QLabel(f"{L['done']} ({len(dn)})"); b.setStyleSheet("font-weight:700"); l.addWidget(b); l.addStretch()
        ck = QCheckBox(L["selall"]); ck.setChecked(bool(dn) and all(x["id"] in s.dsel for x in dn)); ck.toggled.connect(lambda v: (setattr(s, "dsel", {x["id"] for x in dn} if v else set()), s.refresh())); l.addWidget(ck)
        db = QPushButton(L["delsel"]); db.setObjectName("danger"); db.clicked.connect(lambda: s.delete([i for i in s.dsel if s.T(i)], True)); l.addWidget(db); t.setCellWidget(r, 0, w); t.setRowHeight(r, 54)
    # ----- 행 높이
    def on_rowh(s, r, old, new):
        """세로 머리글에서 행 경계선을 끌 때: 그 행(선택된 행을 끌면 선택된 모든 행) 높이 저장"""
        if s.loading or s._rhb: return
        i = s.tb.rid(r); x = s.T(i) if i else None
        if not x: return
        ids = s.sel_ids(); tg = set(ids) if i in ids and len(ids) > 1 else {i}; s._rhb = True
        try:
            x["rowh"] = new
            if len(tg) > 1:
                for rr in range(s.tb.rowCount()):
                    j = s.tb.rid(rr)
                    if j in tg and rr != r: s.tb.setRowHeight(rr, new); s.T(j)["rowh"] = new
        finally:
            s._rhb = False
        s._rhs.start()
    def rowh_dbl(s, r):
        """행 경계선 더블클릭 = 그 행 기본 높이로"""
        i = s.tb.rid(r)
        if i and s.T(i): QTimer.singleShot(0, lambda: s.reset_rowh([i]))
    def reset_rowh(s, ids=None):
        for x in s.d["tasks"]:
            if ids is None or x["id"] in ids: x["rowh"] = 0
        s.save(); s.refresh()
    def ask_rowh(s, title, val, chk=None):
        """행 높이 입력 창 → (값, 체크 여부) / 취소 = None"""
        dl = QDialog(s); dl.setWindowTitle(title); v = QVBoxLayout(dl); f = QFormLayout(); sp = QSpinBox(); sp.setRange(22, 300); sp.setSingleStep(2); sp.setValue(int(val)); sp.setSuffix(" px")
        f.addRow(s.L["rowhq"], sp); v.addLayout(f); ck = None
        if chk: ck = QCheckBox(chk); v.addWidget(ck)
        h = QHBoxLayout(); h.addStretch(); c = QPushButton(s.L["cancel"]); c.clicked.connect(dl.reject); o = QPushButton(s.L["apply"]); o.setObjectName("primary"); o.setDefault(True); o.clicked.connect(dl.accept)
        h.addWidget(c); h.addWidget(o); v.addLayout(h); sp.selectAll()
        return (sp.value(), bool(ck and ck.isChecked())) if dl.exec() else None
    def bulk_rowh(s):
        r = s.ask_rowh(s.L["rowhall"].rstrip("…"), s.d["ui"]["rowh"], s.L["rowhall2"])
        if not r: return
        s.d["ui"]["rowh"] = r[0]
        if r[1]:
            for x in s.d["tasks"]: x["rowh"] = 0
        s.save(); s.refresh()
    def sel_rowh(s):
        ids = s.sel_ids()
        if not ids: return
        x = s.T(ids[0]); r = s.ask_rowh(s.L["rowhsel"].rstrip("…"), x.get("rowh") or s.d["ui"]["rowh"])
        if not r: return
        for i in ids: s.T(i)["rowh"] = r[0]
        s.save(); s.refresh()
    # ----- 행 색상
    def set_color(s, ids, c):
        for i in ids:
            x = s.T(i)
            if x: x["color"] = c
        s.save(); s.refresh()
        if s.side.x and s.side.x["id"] in ids: s.side.show_(s.side.x)
    def fill_color_menu(s, m, ids):
        L = s.L; a = m.addAction(L["rcnone"]); a.triggered.connect(lambda _=False: s.set_color(ids, "")); m.addSeparator()
        for c in PAL: a = m.addAction(sw(c), c); a.triggered.connect(lambda _=False, c=c: s.set_color(ids, c))
        m.addSeparator(); a = m.addAction(L["rcpick"])
        def pick():
            x = s.T(ids[0]) if ids else None; q = QColorDialog.getColor(QColor((x or {}).get("color") or PAL[0]), s)
            if q.isValid(): s.set_color(ids, q.name())
        a.triggered.connect(lambda _=False: pick())
    def row_menu(s):
        """작업 표 우클릭: 행 색상 / 행 높이 / 색상별 정렬"""
        t = s.tb; r = t.rowAt(t.viewport().mapFromGlobal(QCursor.pos()).y()); L = s.L
        if t.rid(r) and not t.selectionModel().isRowSelected(r, QModelIndex()): t.clearSelection(); t.selectRow(r)
        ids = s.sel_ids(); m = QMenu(s)
        if ids:
            s.fill_color_menu(m.addMenu(L["rcol"]), ids); m.addSeparator()
            a = m.addAction(L["rowhsel"]); a.triggered.connect(s.sel_rowh); a = m.addAction(L["rowhrst"]); a.triggered.connect(lambda _=False: s.reset_rowh(set(ids))); m.addSeparator()
        a = m.addAction(L["rowhall"]); a.triggered.connect(s.bulk_rowh)
        a = m.addAction(L["csort"] + ("  ▲" if s.d["ui"]["sort"] == [7, 1] else "  ▼" if s.d["ui"]["sort"] == [7, -1] else "")); a.triggered.connect(lambda _=False: s.cycle_sort(7))
        m.exec(QCursor.pos())
    def view_menu(s):
        m = s.vmenu; m.clear(); L = s.L; ui = s.d["ui"]
        a = m.addAction(L["rowhall"]); a.triggered.connect(s.bulk_rowh)
        a = m.addAction(L["rowhclr"]); a.setEnabled(any(x.get("rowh") for x in s.d["tasks"])); a.triggered.connect(lambda _=False: s.reset_rowh())
        m.addSeparator()
        a = m.addAction(L["csort"] + ("  ▲" if ui["sort"] == [7, 1] else "  ▼" if ui["sort"] == [7, -1] else "")); a.triggered.connect(lambda _=False: s.cycle_sort(7))
        a = m.addAction(L["sclr"]); a.setEnabled(ui["sort"][0] in s.COLS); a.triggered.connect(lambda _=False: s.clear_sort())
        m.addSeparator(); a = m.addAction(L["fall0"]); a.setEnabled(bool(ui.get("flt"))); a.triggered.connect(lambda _=False: s.clear_flt())
        m.addSeparator()
        for k in ("prio", "status"): a = m.addAction(L["lbp" if k == "prio" else "lbs"] + "…"); a.triggered.connect(lambda _=False, k=k: s.edit_labels(k))
    def upd_viewbtn(s):
        if not hasattr(s, "vbn"): return
        n = len(s.d["ui"].get("flt") or {}); s.vbn.setText("▤  " + s.L["view"] + (f" · {s.L['fltn'].format(n=n)}" if n else "") + "  ▾")
        s.vbn.setProperty("on", bool(n)); s.vbn.style().unpolish(s.vbn); s.vbn.style().polish(s.vbn)
    # ----- 동작
    def on_sel(s):
        """선택만으로는 사이드바를 열지 않음. 이미 열려 있으면 선택한 작업으로 내용만 바꿈"""
        if s.loading or not s.side.x: return
        ids = s.sel_ids()
        if len(ids) == 1 and s.T(ids[0]) and s.side.x["id"] != ids[0]: s.side.show_(s.T(ids[0]))
    def title_click(s, r, c):
        """테이블에서 제목(작업명) 셀을 클릭했을 때만 사이드바 열기 (Ctrl/Shift 다중 선택 중엔 열지 않음)"""
        if c != 1 or QApplication.keyboardModifiers() != Qt.KeyboardModifier.NoModifier: return
        it = s.tb.item(r, 1)
        if it and s.T(it.data(Qt.ItemDataRole.UserRole)): s.side.show_(s.T(it.data(Qt.ItemDataRole.UserRole)))
    def open_task(s, i, focus=False):
        """간트/캘린더/타임라인/카드 뷰에서 제목 클릭 → 테이블 선택 동기화 + 사이드바 열기"""
        x = s.T(i)
        if not x: return
        s.loading = True; s.tb.clearSelection(); s.select(i); s.loading = False; s.side.show_(x)
        if focus: s.side.name.setFocus()
    # ----- 검색 / 태그 필터
    def set_q(s, t): s.q = t; s.refresh()
    def all_tags(s):
        f = s.d["ui"].get("folder", ""); out = set()
        if f == TRASH: return []
        for t in s.d["tasks"]:
            if not f or t.get("folder", "") == f: out.update(t["tags"])
        return sorted(out, key=nat)
    def tag_menu(s):
        m = s.tmenu; m.clear(); L = s.L; ui = s.d["ui"]; tags = s.all_tags(); sel = [g for g in ui.get("tagf", []) if g in tags]
        if sel != ui.get("tagf", []): ui["tagf"] = sel; s.save(); s.refresh()
        if not tags: a = m.addAction(L["notag"]); a.setEnabled(False)
        for g in tags:
            a = m.addAction("# " + g); a.setCheckable(True); a.setChecked(g in sel); a.toggled.connect(lambda v, g=g: s.tog_tag(g, v))
        m.addSeparator(); a = m.addAction(L["tagand"]); a.setCheckable(True); a.setChecked(bool(ui.get("tagand"))); a.toggled.connect(s.set_tagand)
        s._clr = m.addAction(L["tagall"]); s._clr.setEnabled(bool(sel)); s._clr.triggered.connect(lambda: s.set_tagf([]))
    def tog_tag(s, g, on):
        tf = [x for x in s.d["ui"].get("tagf", []) if x != g] + ([g] if on else []); s.set_tagf(tf)
        if getattr(s, "_clr", None): s._clr.setEnabled(bool(tf))
    def set_tagf(s, tf): s.d["ui"]["tagf"] = tf; s.save(); s.refresh()
    def set_tagand(s, v): s.d["ui"]["tagand"] = bool(v); s.save(); s.refresh()
    def upd_tagbtn(s):
        if not hasattr(s, "tbn"): return
        tf = s.d["ui"].get("tagf") or []; j = ", ".join(tf); j = j if len(j) <= 18 else j[:17] + "…"
        s.tbn.setText("#  " + s.L["tagf"] + (f" · {j}" if tf else "") + "  ▾"); s.tbn.setToolTip(", ".join(tf))
        s.tbn.setProperty("on", bool(tf)); s.tbn.style().unpolish(s.tbn); s.tbn.style().polish(s.tbn)
    def select(s, i):
        for r in range(s.tb.rowCount()):
            it = s.tb.item(r, 1)
            if it and it.data(Qt.ItemDataRole.UserRole) == i: s.tb.selectRow(r); return
    def item_changed(s, it):
        if s.loading: return
        x = s.T(it.data(Qt.ItemDataRole.UserRole))
        if not x: return
        if it.column() == 1: x["name"] = it.text()
        else: x["tags"] = [a.strip() for a in it.text().split(",") if a.strip()]
        s.save(); s.views()
        if s.side.x is x: s.side.show_(x)
    def setf(s, x, k, i):
        if i is None: return
        was = s.is_done(x); x[k] = i
        if k == "status":
            if s.is_done(x): x["done_at"] = x.get("done_at") if was and x.get("done_at") else time.time()
            else: x["done_at"] = 0
        s.save(); s.refresh()
        if s.side.x is x: s.side.show_(x)
    def add(s, after=None, **kw):
        # 새 작업은 현재 태그 필터의 태그를 물려받고, 검색어는 지움 (새 작업이 필터에 가려지지 않도록)
        if s.q: s.q = ""; s.search.blockSignals(True); s.search.clear(); s.search.blockSignals(False)
        if s.d["ui"].get("folder") == TRASH: s.d["ui"]["folder"] = ""; s.fp.sync()
        x = dict(id=uuid.uuid4().hex[:8], name="", prio=s.ldef("prio"), status=s.ldef("status"), due="", start="", end="", tags=list(s.d["ui"].get("tagf") or []), memo="", pin=False, done_at=0,
                 folder=s.d["ui"]["folder"], color="", rowh=0); L = s.d["tasks"]; s.keep.add(x["id"])   # 열 필터가 걸려 있어도 새 작업은 보이게
        tab = s.d["ui"]["tab"]
        if tab in (1, 2, 3) and not kw:   # 간트·캘린더·타임라인은 날짜가 있어야 보이므로 오늘(캘린더는 보고 있는 달)로 시작
            td = date.today(); dd = td if (tab != 2 or (td.year, td.month) == (s.cal.year, s.cal.month)) else s.cal; x["start"] = x["end"] = dd.isoformat()
        for k, v in kw.items():
            if k in x: x[k] = v
        if s.is_done(x): x["done_at"] = time.time()
        L.insert(next((k + 1 for k, y in enumerate(L) if y["id"] == after), len(L)), x); s.save()
        if tab != 0: s.refresh(); s.open_task(x["id"], True); return   # 보던 뷰에 그대로 머물며 편집 사이드바에서 이름 입력
        s.switch(0, False); s.refresh(); s.select(x["id"])
        for r in range(s.tb.rowCount()):
            it = s.tb.item(r, 1)
            if it and it.data(Qt.ItemDataRole.UserRole) == x["id"]: s.tb.scrollToItem(it); s.tb.editItem(it); break
    def delete(s, ids, ask=False):
        ids = [i for i in ids if s.T(i)]
        if not ids or (ask and QMessageBox.question(s, "?", s.L["ask"]) != QMessageBox.StandardButton.Yes): return
        idset = set(ids); now = time.time(); L = s.d["tasks"]; moved = []
        for k, t in enumerate(L):   # 원래 위치(순번 + 바로 앞 작업)를 기억해 둠 → 복구 시 같은 자리로
            if t["id"] in idset: moved.append(dict(t, deleted_at=now, pos=k, after=L[k - 1]["id"] if k else ""))
        s.d["trash"] = moved + s.d["trash"]; s.d["tasks"] = [t for t in L if t["id"] not in idset]; s.dsel -= idset
        if s.side.x and s.side.x["id"] in idset: s.side.close_()
        s.save(); s.refresh()
    # ----- 휴지통
    def trash_vis(s):
        qs = s.q.lower().split(); out = []
        for t in s.d["trash"]:
            if qs:
                hay = (t["name"] + "\n" + t["memo"] + "\n" + " ".join(t["tags"])).lower()
                if not all(q in hay for q in qs): continue
            out.append(t)
        return sorted(out, key=lambda x: -x.get("deleted_at", 0))
    def restore(s, ids):
        """휴지통 → 원래 폴더의 원래 자리로 복구 (폴더가 지워졌으면 '전체'). 최근에 지운 것부터 되돌려 순서 유지"""
        ids = set(ids); xs = sorted([x for x in s.d["trash"] if x["id"] in ids], key=lambda x: (-x.get("deleted_at", 0), x.get("pos", 0)))
        if not xs: return
        ok = {f["id"] for f in s.d["folders"]}; L = s.d["tasks"]; used = {t["id"] for t in L}
        for x in xs:
            t = {k: v for k, v in x.items() if k not in ("deleted_at", "pos", "after")}
            if t.get("folder", "") not in ok: t["folder"] = ""
            while t["id"] in used: t["id"] = uuid.uuid4().hex[:8]
            used.add(t["id"]); af = x.get("after")
            at = next((k + 1 for k, y in enumerate(L) if y["id"] == af), None) if af else None
            L.insert(min(x.get("pos", 0), len(L)) if at is None else at, t)
        s.d["trash"] = [x for x in s.d["trash"] if x["id"] not in ids]; s.save(); s.refresh()
    def purge(s, ids):
        ids = set(ids) & {x["id"] for x in s.d["trash"]}
        if not ids or QMessageBox.question(s, "?", s.L["askpurge"].format(n=len(ids))) != QMessageBox.StandardButton.Yes: return
        s.d["trash"] = [x for x in s.d["trash"] if x["id"] not in ids]; s.save(); s.refresh()
    def empty_trash(s):
        n = len(s.d["trash"])
        if not n or QMessageBox.question(s, "?", s.L["askempty"].format(n=n)) != QMessageBox.StandardButton.Yes: return
        s.d["trash"] = []; s.save(); s.refresh()
    # ----- 테이블 단축키 / 드래그 이동
    def del_sel(s):
        """Delete 키: 선택한 작업 삭제 후 그 자리의 다음 작업을 선택"""
        ids = s.sel_ids()
        if not ids: return
        if CONFIRM_DELETE and QMessageBox.question(s, "?", s.L["askdel"].format(n=len(ids))) != QMessageBox.StandardButton.Yes: return
        rows = [r for r in range(s.tb.rowCount()) if s.tb.rid(r) in ids]; top = min(rows) if rows else 0
        s.delete(ids)
        r = top if s.tb.rid(top) else top - 1
        if r >= 0 and s.tb.rid(r):
            s.tb.selectRow(r); s.tb.selectionModel().setCurrentIndex(s.tb.model().index(r, 1), QItemSelectionModel.SelectionFlag.NoUpdate)
        s.tb.setFocus()
    def copy_tasks(s):
        """Ctrl+C: 선택 작업을 클립보드에 (앱 전용 형식 + 작업명 텍스트)"""
        xs = [json.loads(json.dumps(s.T(i), ensure_ascii=False)) for i in s.sel_ids() if s.T(i)]
        if not xs: return
        md = QMimeData(); md.setData(MIME, QByteArray(json.dumps(xs, ensure_ascii=False).encode("utf-8"))); md.setText("\n".join(x["name"] for x in xs))
        QApplication.clipboard().setMimeData(md)
    def paste_tasks(s):
        """Ctrl+V: 복사한 작업을 선택 위치 뒤에 새 작업으로 추가 (일반 텍스트는 한 줄 = 작업 1개)"""
        md = QApplication.clipboard().mimeData(); raw = []; fid = s.d["ui"].get("folder", ""); fid = "" if fid == TRASH else fid
        if md is None: return
        if md.hasFormat(MIME):
            try: raw = json.loads(bytes(md.data(MIME)).decode("utf-8"))
            except Exception: raw = []
            raw = [dict(t, id="", folder=fid or t.get("folder", "")) for t in raw if isinstance(t, dict)] if isinstance(raw, list) else []
        elif md.hasText():
            tg = list(s.d["ui"].get("tagf") or [])
            raw = [dict(name=ln.strip(), tags=tg, folder=fid) for ln in md.text().splitlines() if ln.strip()][:200]
            if raw and s.q: s.q = ""; s.search.blockSignals(True); s.search.clear(); s.search.blockSignals(False)
        if not raw: return
        used = {t["id"] for t in s.d["tasks"]}; new = [x for x in (norm_task(t, used) for t in raw) if x]
        ok = {f["id"] for f in s.d["folders"]}
        for x in new:
            if x["folder"] not in ok: x["folder"] = ""
            s.lab_fix(x); x["done_at"] = time.time() if s.is_done(x) else 0; s.keep.add(x["id"])
        sel = set(s.sel_ids()); L = s.d["tasks"]
        at = max((k for k, t in enumerate(L) if t["id"] in sel), default=len(L) - 1) + 1
        L[at:at] = new; s.save(); s.switch(0, False); s.refresh()
        t = s.tb; t.clearSelection(); ids = {x["id"] for x in new}; first = None
        for r in range(t.rowCount()):
            if t.rid(r) in ids:
                t.selectionModel().select(t.model().index(r, 0), QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)
                if first is None: first = r
        if first is not None:
            t.selectionModel().setCurrentIndex(t.model().index(first, 1), QItemSelectionModel.SelectionFlag.NoUpdate); t.scrollTo(t.model().index(first, 1))
        t.setFocus()
    def rename_sel(s):
        """F2: 현재(또는 첫 번째 선택) 작업의 이름을 바로 편집"""
        t = s.tb; r = t.currentRow()
        if not (t.rid(r) and t.selectionModel().isRowSelected(r, QModelIndex())):
            ids = s.sel_ids(); r = next((k for k in range(t.rowCount()) if ids and t.rid(k) == ids[0]), -1)
        it = t.item(r, 1) if r >= 0 else None
        if not it or not t.rid(r): return
        t.selectionModel().setCurrentIndex(t.model().index(r, 1), QItemSelectionModel.SelectionFlag.NoUpdate)
        t.scrollToItem(it); s.nd.ren = True; t.editItem(it)
    def move_tasks(s, ids, k):
        """드래그 이동: 진행 중 목록의 k번째 위치로 ids를 옮기고 수동 정렬로 전환.
        고정(📌) 작업 사이에 놓으면 고정, 일반 작업 사이에 놓으면 고정 해제"""
        t = s.tb; act = [t.rid(r) for r in range(s.nact)]; ids = [i for i in act if i in set(ids)]
        if not ids: return
        rest = [i for i in act if i not in ids]; pos = len([i for i in act[:k] if i not in ids]); new = rest[:pos] + ids + rest[pos:]
        P = sum(1 for i in rest if s.T(i)["pin"]); pinchg = False
        if pos != P:
            for i in ids:
                if s.T(i)["pin"] != (pos < P): s.T(i)["pin"] = pos < P; pinchg = True
        if new == act and not pinchg and s.d["ui"]["sort"][0] not in s.COLS: return
        L = s.d["tasks"]; aset = set(act); slots = [n for n, x in enumerate(L) if x["id"] in aset]; by = {x["id"]: x for x in L}
        for n, i in zip(slots, new): L[n] = by[i]
        s.d["ui"]["sort"] = [0, 1]; s.save(); s.refresh()
        r0 = next((r for r in range(t.rowCount()) if t.rid(r) == ids[0]), None)
        if r0 is not None: t.selectionModel().setCurrentIndex(t.model().index(r0, 1), QItemSelectionModel.SelectionFlag.NoUpdate)
    def pick(s, x, k):
        dl = DateDlg(s, x[k], s.L)
        if dl.exec() and dl.res is not None: s.setd(x, k, dl.res)
    def setd(s, x, k, v):
        x[k] = v
        if x["start"] and x["end"] and x["end"] < x["start"]: x["end" if k == "start" else "start"] = v
        s.save(); s.refresh()
        if s.side.x is x: s.side.show_(x)
    def pickrange(s, x):
        for k in ("start", "end"):
            dl = DateDlg(s, x[k], s.L); dl.setWindowTitle(s.L[k])
            if not (dl.exec() and dl.res is not None): return
            s.setd(x, k, dl.res)
    # ----- 폴더
    def toggle_folders(s):
        on = not s.d["ui"].get("fold", False); s.d["ui"]["fold"] = on; s.fp.slide(not on); s.save()
    def set_ficon(s, fid):
        if fid == TRASH:
            dl = EmojiDlg(s, s.d["ui"].get("trashicon", ""), s.L, s.L["trash"] + " · " + s.L["icon"])
            if dl.exec() and dl.res is not None: s.d["ui"]["trashicon"] = dl.res; s.save(); s.fp.upd_trash()
            return
        f = next((f for f in s.d["folders"] if f["id"] == fid), None) if fid else None
        if fid and not f: return
        dl = EmojiDlg(s, f.get("icon", "") if f else s.d["ui"].get("allicon", ""), s.L)
        if not dl.exec() or dl.res is None: return
        if f: f["icon"] = dl.res
        else: s.d["ui"]["allicon"] = dl.res
        s.save(); s.fp.reload()
        if s.side.x: s.side.show_(s.side.x)
    def set_folder(s, fid):
        if s.d["ui"].get("folder", "") == fid: return
        s.d["ui"]["folder"] = fid
        if fid != TRASH: tags = set(s.all_tags()); s.d["ui"]["tagf"] = [g for g in s.d["ui"].get("tagf", []) if g in tags]
        s.dsel.clear(); s.tb.clearSelection(); s.side.close_(); s.save(); s.refresh(); s.fp.sync()
    def add_folder(s):
        f = dict(id=uuid.uuid4().hex[:8], name=s.L["newf"]); s.d["folders"].append(f); s.set_folder(f["id"]); s.fp.reload(edit=f["id"])
    def del_folder(s, fid):
        if QMessageBox.question(s, "?", s.L["askf"]) != QMessageBox.StandardButton.Yes: return
        for t in s.d["tasks"]:
            if t.get("folder", "") == fid: t["folder"] = ""
        s.d["folders"] = [f for f in s.d["folders"] if f["id"] != fid]
        if s.d["ui"]["folder"] == fid: s.d["ui"]["folder"] = ""
        s.dsel.clear(); s.tb.clearSelection(); s.side.close_(); s.save(); s.refresh(); s.fp.reload()
    def setfolder(s, x, fid):
        x["folder"] = fid or ""; s.save(); cur = s.d["ui"]["folder"]
        if cur and x["folder"] != cur: s.tb.clearSelection(); s.side.close_()
        s.refresh()
    # ----- 설정 / 작업 데이터 입출력
    def import_tasks(s, par):
        L = s.L; p, _ = QFileDialog.getOpenFileName(par, L["ftask"] + " · " + L["imp"], "", "JSON (*.json)")
        if not p: return False
        try:
            with open(p, encoding="utf-8") as fh: j = json.load(fh)
            raw = j["tasks"]; assert isinstance(raw, list)
            used = set(); new = [x for x in (norm_task(t, used) for t in raw) if x]; nf = norm_folders(j.get("folders"), L["newf"])
            ht = isinstance(j.get("trash"), list); nt = [x for x in (norm_trash(t, used) for t in (j.get("trash") if ht else [])) if x]
            nl = norm_labels(j.get("labels"), s.d["theme"]) if isinstance(j.get("labels"), dict) else None
        except Exception:
            QMessageBox.warning(par, L["err"], L["badtask"]); return False
        m = QMessageBox(par); m.setWindowTitle(L["ftask"]); m.setText(L["impq"])
        a = m.addButton(L["merge"], QMessageBox.ButtonRole.AcceptRole); b = m.addButton(L["replace"], QMessageBox.ButtonRole.DestructiveRole); m.addButton(QMessageBox.StandardButton.Cancel); m.exec()
        c = m.clickedButton()
        if c is None or (c != a and c != b): return False
        if c == b:
            s.d["tasks"] = new; s.d["folders"] = nf
            if ht: s.d["trash"] = nt
            if nl: s.d["labels"] = nl
        else:
            for k in ("prio", "status") if nl else ():   # 합치기: 파일에만 있는 레이블을 뒤에 추가
                have = {l["id"] for l in s.LB(k)}; s.LB(k).extend(l for l in nl[k]["items"] if l["id"] not in have)
            tx = {t["id"]: k for k, t in enumerate(s.d["trash"])}
            for t in nt:
                if t["id"] in tx: s.d["trash"][tx[t["id"]]] = t
                else: s.d["trash"].append(t)
            ix = {t["id"]: k for k, t in enumerate(s.d["tasks"])}
            for t in new:
                if t["id"] in ix: s.d["tasks"][ix[t["id"]]] = t
                else: s.d["tasks"].append(t)
            fx = {f["id"]: f for f in s.d["folders"]}
            for f in nf:
                if f["id"] in fx: fx[f["id"]].update(f)
                else: s.d["folders"].append(f)
        ok = {f["id"] for f in s.d["folders"]}
        for t in s.d["tasks"]:
            if t.get("folder", "") not in ok: t["folder"] = ""
        for t in s.d["tasks"] + s.d["trash"]: s.lab_fix(t)
        if s.d["ui"].get("folder", "") not in ok and s.d["ui"].get("folder") != TRASH: s.d["ui"]["folder"] = ""
        s.dsel.clear(); s.save(); QMessageBox.information(par, L["ftask"], L["impok"].format(n=len(new))); return True
    # ----- 설정 / 백업
    def settings(s):
        L = s.L; V = json.loads(json.dumps(s.d["theme"])); dlg = QDialog(s); dlg.setWindowTitle(L["settings"]); f = QFormLayout(dlg); names = {"한국어": "ko", "English": "en", "日本語": "ja"}
        lg = QComboBox(); lg.addItems(names); lg.setCurrentText(next(k for k, v in names.items() if v == s.d["lang"])); f.addRow(L["lang"], lg); cbs = {}
        # ----- 테마: 기본 테마 / 내장 테마 / 사용자 테마 드롭다운. 고르면 아래 색 4개가 바뀌고 [적용]을 눌러야 반영됨
        tcb = QComboBox(); tcb.setMinimumWidth(220); tsv = QPushButton(L["th_save"]); tdl = QPushButton(L["th_del"])
        for b in (tsv, tdl): b.setAutoDefault(False)
        tcw = QWidget(); tch = QHBoxLayout(tcw); tch.setContentsMargins(0, 0, 0, 0); tch.setSpacing(4); tch.addWidget(tcb, 1); tch.addWidget(tsv); tch.addWidget(tdl); f.addRow(L["theme"], tcw)
        def ut(): return clean_ut(s.d["ui"].get("usrthemes"))
        def tcols(k):
            if k == "d": return tuple(QColor(DT[x]).name() for x in TKEYS)
            if k.startswith("b:"): c = BT.get(k[2:])
            elif k.startswith("u:"): c = ut().get(k[2:])
            else: c = None
            return tuple(QColor(c[x]).name() for x in TKEYS) if c else None
        def curc(): return tuple(QColor(cbs[x].c).name() for x in TKEYS)
        def tfill(sel=None):
            U = ut(); keys = ["d"] + ["b:" + n for n in BT] + ["u:" + n for n in U]; now = curc()
            k = next((x for x in (sel, s.d["ui"].get("themekey")) if x in keys and tcols(x) == now), None) or next((x for x in keys if tcols(x) == now), None)
            tcb.blockSignals(True); tcb.clear()
            if k is None: tcb.addItem(L["th_cus"], "c")
            for x in keys[:1 + len(BT)]: tcb.addItem(tsw(tcols(x)), L["th_def"] if x == "d" else x[2:], x)
            if U:
                tcb.insertSeparator(tcb.count())
                for x in keys[1 + len(BT):]: tcb.addItem(tsw(tcols(x)), "★ " + x[2:], x)
            tcb.setCurrentIndex(tcb.findData(k or "c")); tcb.blockSignals(False); tdl.setEnabled(bool(k and k.startswith("u:")))
        def tpick(i):
            c = tcols(tcb.itemData(i) or "c")
            if c is None: return
            for x, v in zip(TKEYS, c): cbs[x].c = v; cbs[x].pa()
            tfill(tcb.itemData(i))
        def tsave():
            U = ut(); n, ok = QInputDialog.getText(dlg, L["th_save"], L["th_name"]); n = n.strip()[:30]
            if not ok or not n: return
            if n in BT or n in {TR[g]["th_def"] for g in TR}: QMessageBox.warning(dlg, L["err"], L["th_resv"]); return
            if n in U and QMessageBox.question(dlg, L["th_save"], L["th_over"].format(n=n)) != QMessageBox.StandardButton.Yes: return
            U[n] = dict(zip(TKEYS, curc())); s.d["ui"]["usrthemes"] = U; s.save(); tfill("u:" + n)
        def tdel():
            k = tcb.currentData()
            if not (isinstance(k, str) and k.startswith("u:")): return
            if QMessageBox.question(dlg, L["th_del"], L["th_delq"].format(n=k[2:])) != QMessageBox.StandardButton.Yes: return
            U = ut(); U.pop(k[2:], None); s.d["ui"]["usrthemes"] = U; s.save(); tfill()
        tcb.activated.connect(tpick); tsv.clicked.connect(tsave); tdl.clicked.connect(tdel)
        for i, k in enumerate(("bg", "panel", "fg", "accent")): cbs[k] = ColorBtn(V[k]); f.addRow(L["cn"][i], cbs[k]); cbs[k].clicked.connect(lambda _=False: tfill())   # 색을 직접 바꾸면 '사용자 지정'으로 표시
        tfill()
        lbw = QWidget(); lbh = QHBoxLayout(lbw); lbh.setContentsMargins(0, 0, 0, 0); lbh.setSpacing(4)   # 우선순위/상태 이름·색·순서는 레이블 편집기에서
        for k in ("prio", "status"):
            b = QPushButton(L["lbp" if k == "prio" else "lbs"] + "…"); b.setAutoDefault(False); b.clicked.connect(lambda _=False, k=k: s.edit_labels(k, dlg)); lbh.addWidget(b)
        f.addRow(L["labels"], lbw)
        fp = FontPicker(V["font"], L); f.addRow(L["font"], fp); sz = QSpinBox(); sz.setRange(8, 24); sz.setValue(V["size"]); f.addRow(L["size"], sz)
        # 고정핀 이모지
        pv = [V.get("pin") or DEFPIN]; pbn = QPushButton(pv[0]); pbn.setAutoDefault(False); pbn.setFixedWidth(64); pbn.setStyleSheet("font-size:14pt;padding:2px")
        def pkpin():
            dl = EmojiDlg(dlg, pv[0], L, L["pinemo"])
            if dl.exec() and dl.res is not None: pv[0] = dl.res or DEFPIN; pbn.setText(pv[0])
        pbn.clicked.connect(pkpin); f.addRow(L["pinemo"], pbn)
        def collect():
            T = json.loads(json.dumps(V))
            for k, b in cbs.items(): T[k] = b.c
            T["font"] = fp.family(); T["size"] = sz.value(); T["pin"] = pv[0]
            return T, names[lg.currentText()]
        def apply():
            s.d["theme"], s.d["lang"] = collect(); k = tcb.currentData(); s.d["ui"]["themekey"] = k if isinstance(k, str) and k != "c" else ""; s.save(); dlg.accept(); s.build()
        def reset(): s.d["theme"] = json.loads(json.dumps(DT)); s.d["ui"]["themekey"] = "d"; s.save(); dlg.accept(); s.build()
        def save_json(title, name, obj):
            p, _ = QFileDialog.getSaveFileName(dlg, title, f"{name}-{date.today():%Y%m%d}.json", "JSON (*.json)")
            if not p: return
            try:
                with open(p, "w", encoding="utf-8") as fh: json.dump(obj, fh, ensure_ascii=False, indent=1)
            except Exception as e: QMessageBox.warning(dlg, L["err"], str(e))
        def exp_set(): T, lang = collect(); save_json(L["fset"] + " · " + L["exp"], "todo-settings", dict(kind="todo-settings", version=1, lang=lang, theme=T, usrthemes=ut()))
        def imp_set():
            p, _ = QFileDialog.getOpenFileName(dlg, L["fset"] + " · " + L["imp"], "", "JSON (*.json)")
            if not p: return
            try:
                with open(p, encoding="utf-8") as fh: j = json.load(fh)
                th = clean_theme(j.get("theme")); lang = j.get("lang") if j.get("lang") in TR else None
                us = clean_ut(j.get("usrthemes"))
                if th is None and lang is None and not us: raise ValueError
            except Exception: QMessageBox.warning(dlg, L["err"], L["badset"]); return
            s.d["theme"].update(th or {})
            if us: s.d["ui"]["usrthemes"] = dict(ut(), **us)
            if lang: s.d["lang"] = lang
            s.save(); dlg.accept(); s.build()
        def exp_task(): save_json(L["ftask"] + " · " + L["exp"], "todo-tasks", dict(kind="todo-tasks", version=2, folders=s.d["folders"], tasks=s.d["tasks"], trash=s.d["trash"], labels=s.d["labels"]))
        def imp_task():
            if s.import_tasks(dlg): dlg.accept(); s.build()
        def btns(*items):
            h = QHBoxLayout()
            for tx, fn, ob in items: b = QPushButton(tx); b.setObjectName(ob); b.clicked.connect(fn); h.addWidget(b)
            return h
        # 설정 / 데이터 파일 경로
        def chpath(key, np=None):
            old = s.P[key]; other = s.P["data" if key == "settings" else "settings"]; ttl = L["ppath" if key == "settings" else "dpath"]
            if np is None:
                np, _ = QFileDialog.getSaveFileName(dlg, ttl, old, "JSON (*.json)", options=QFileDialog.Option.DontConfirmOverwrite)
                if not np: return
            np = os.path.abspath(os.path.expanduser(np))
            if same_path(np, old): return
            load = False
            if os.path.exists(np) and not same_path(np, other):
                j = read_json(np)
                if not (has_set if key == "settings" else has_data)(j):
                    QMessageBox.warning(dlg, L["err"], L["badset" if key == "settings" else "badtask"]); return
                m = QMessageBox(dlg); m.setWindowTitle(ttl); m.setText(L["pathq"]); a = m.addButton(L["imp"], QMessageBox.ButtonRole.AcceptRole)
                b = m.addButton(L["replace"], QMessageBox.ButtonRole.DestructiveRole); m.addButton(QMessageBox.StandardButton.Cancel); m.exec(); c = m.clickedButton()
                if c is None or (c != a and c != b): return
                load = c == a
            snap = json.dumps(s.d, ensure_ascii=False); s.d["theme"], s.d["lang"] = collect(); s.P[key] = np   # 창에서 바꾼 값도 함께 적용
            if load:
                if key == "settings": s.load_set(j)
                else: s.load_data(j)
                s.fixup()
            try: s.save(strict=True)
            except Exception as e:
                s.P[key] = old; s.d = json.loads(snap); s.side.close_(); QMessageBox.warning(dlg, L["err"], L["badpath"] + "\n\n" + str(e)); return
            try: write_json(PATHS, dict(settings=s.P["settings"], data=s.P["data"]))
            except Exception: pass
            s.dsel.clear(); dlg.accept(); s.build()
        def path_row(key):
            wd = QWidget(); h = QHBoxLayout(wd); h.setContentsMargins(0, 0, 0, 0); h.setSpacing(4)
            e = QLineEdit(s.P[key]); e.setReadOnly(True); e.setMinimumWidth(280); e.setToolTip(s.P[key]); e.setCursorPosition(0); h.addWidget(e, 1)
            for tx, fn in ((L["chg"], lambda: chpath(key)), (L["deflt"], lambda: chpath(key, FILE)),
                           (L["opendir"], lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(s.P[key]))))):
                b = QPushButton(tx); b.setAutoDefault(False); b.clicked.connect(fn); h.addWidget(b)
            return wd
        f.addRow(hr()); f.addRow(L["ppath"], path_row("settings")); f.addRow(L["dpath"], path_row("data"))
        f.addRow(L["fset"], btns((L["exp"], exp_set, ""), (L["imp"], imp_set, "")))
        f.addRow(L["ftask"], btns((L["exp"], exp_task, ""), (L["imp"], imp_task, "")))
        f.addRow(btns((L["apply"], apply, "primary"), (L["reset"], reset, ""))); dlg.exec()


def _hook(t, v, tb):
    import traceback; traceback.print_exception(t, v, tb)
    try: QMessageBox.warning(None, "Error", f"{t.__name__}: {v}")
    except Exception: pass


if __name__ == "__main__":
    sys.excepthook = _hook
    app = QApplication(sys.argv); app.setStyle("Fusion"); w = Win(); w.show(); sys.exit(app.exec())