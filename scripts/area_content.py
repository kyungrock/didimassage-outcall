#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""지역별 SEO 콘텐츠(고유 문단, 우편번호, 키워드 H3) 생성"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AreaContent:
    highlights: list[str]
    why_titles: list[str]
    postal_code: str
    address_locality: str
    street_address: str
    course_prefix: str
    service_tips: list[tuple[str, str]] | None = None
    local_notes: list[tuple[str, str]] | None = None


# 구·시 대표 우편번호 (서비스 지역 기준)
POSTAL_CODES: dict[str, str] = {
    "seoul-gangnam": "06236",
    "seoul-gangdong": "05200",
    "seoul-gangbuk": "01100",
    "seoul-gangseo": "07500",
    "seoul-gwanak": "08700",
    "seoul-gwangjin": "05000",
    "seoul-guro": "08300",
    "seoul-geumcheon": "08500",
    "seoul-nowon": "01600",
    "seoul-dobong": "01300",
    "seoul-dongdaemun": "02500",
    "seoul-dongjak": "06900",
    "seoul-mapo": "03900",
    "seoul-seodaemun": "03700",
    "seoul-seocho": "06500",
    "seoul-seongdong": "04700",
    "seoul-seongbuk": "02800",
    "seoul-songpa": "05500",
    "seoul-yangcheon": "07900",
    "seoul-yeongdeungpo": "07200",
    "seoul-yongsan": "04300",
    "seoul-eunpyeong": "03300",
    "seoul-jongno": "03100",
    "seoul-jung": "04500",
    "seoul-jungnang": "02100",
    "gyeonggi-suwon": "16400",
    "gyeonggi-seongnam": "13400",
    "gyeonggi-goyang": "10300",
    "gyeonggi-yongin": "16900",
    "gyeonggi-bucheon": "14500",
    "gyeonggi-ansan": "15300",
    "gyeonggi-anyang": "13900",
    "gyeonggi-namyangju": "12200",
    "gyeonggi-hwaseong": "18200",
    "gyeonggi-pyeongtaek": "17700",
    "gyeonggi-uijeongbu": "11600",
    "gyeonggi-siheung": "14900",
    "gyeonggi-paju": "10800",
    "gyeonggi-gimpo": "10000",
    "gyeonggi-gwangmyeong": "14200",
    "gyeonggi-gwangju-si": "12700",
    "gyeonggi-hanam": "12900",
    "gyeonggi-osan": "18100",
    "gyeonggi-icheon": "17300",
    "gyeonggi-guri": "11900",
    "incheon-namdong": "21500",
    "incheon-bupyeong": "21300",
    "incheon-yeonsu": "21900",
    "incheon-seogu": "22600",
    "incheon-jung": "22300",
    "incheon-gyeyang": "21000",
    "incheon-michuhol": "22100",
    "busan-haeundae": "48000",
    "busan-suyeong": "48200",
    "busan-busanjin": "47200",
    "busan-dongnae": "47700",
    "busan-nam": "48400",
    "busan-sasang": "46900",
    "busan-buk": "46500",
    "daegu-suseong": "42000",
    "daegu-dalseo": "42700",
    "daegu-jung": "41900",
    "daegu-dong": "41200",
    "daegu-nam": "42400",
    "daejeon-yuseong": "34000",
    "daejeon-seo": "35200",
    "daejeon-dong": "34600",
    "daejeon-jung": "34900",
    "gwangju-seo": "61900",
    "gwangju-nam": "61700",
    "gwangju-buk": "61000",
    "gwangju-dong": "61400",
    "jeju-si": "63100",
    "jeju-seogwipo": "63500",
    "ulsan-nam": "44700",
    "ulsan-jung": "44400",
    "ulsan-buk": "44200",
    "gyeonggi-paju-unjeong": "10800",
    "gyeonggi-paju-geumchon": "10800",
    "gyeonggi-paju-gyoha": "10800",
    "gyeonggi-paju-munsan": "10800",
}

# 슬러그별 지역 특화 문단 (1~2문단)
HIGHLIGHTS: dict[str, list[str]] = {
    "seoul-gangnam": [
        "강남 테헤란로 인근 호텔, 삼성동 오피스텔 등 강남의 특성에 맞춰 신속하게 찾아갑니다.",
        "역삼·논현·청담·삼성동 비즈니스 지구에서 야근 후 호텔·오피스텔 출장 문의가 많으며, 대치·신사 일대 주거·상업 지역도 24시간 배정이 가능합니다.",
    ],
    "seoul-yeongdeungpo": [
        "여의도 금융가 오피스·인근 호텔, 당산·문래 오피스텔까지 여의도 출장 특성에 맞게 동선을 최적화해 방문합니다.",
        "영등포역·당산역 인근 숙박시설과 주거 단지에서 퇴근 후·출장 중 당일 예약 문의가 이어집니다.",
    ],
    "seoul-mapo": [
        "홍대·합정·연남·망원 상권의 게스트하우스·소형 호텔, 공덕·마포 오피스텔까지 홍대권 특성에 맞춰 배정합니다.",
        "망원·연남 카페거리 인근 숙소와 자택에서 늦은 시간 출장마사지 상담이 많은 지역입니다.",
    ],
    "seoul-songpa": [
        "잠실 롯데월드·석촌호수 인근 호텔, 방이·문정 오피스텔 등 송파 대형 단지에 맞춰 신속 방문합니다.",
        "가락·석촌동 주거 밀집 지역과 잠실 비즈니스 호텔에서 당일·야간 예약이 가능합니다.",
    ],
    "seoul-jung": [
        "명동·을지로·충무로 호텔가와 회현·남대문 인근 숙박시설에 서울 도심 출장 특화로 빠르게 찾아갑니다.",
        "관광·출장객이 많은 중구 일대에서 호텔 룸서비스형 출장마사지 문의가 집중됩니다.",
    ],
    "seoul-guro": [
        "구로디지털단지·신도림역 인근 오피스텔, 가리봉·구로 주거지까지 IT·제조 업무지 특성에 맞춰 배정합니다.",
        "야근이 잦은 구로·신도림 일대에서 퇴근 후 당일 출장 예약이 많습니다.",
    ],
    "seoul-geumcheon": [
        "가산디지털단지 오피스·독산·시흥 주거 단지 등 금천권 업무·주거 혼합 지역에 맞춰 방문합니다.",
        "가산역 인근 비즈니스 호텔과 오피스텔에서 출장 후 피로 회복 문의가 이어집니다.",
    ],
    "seoul-seocho": [
        "서초·방배·잠원 주거지와 양재·교대 인근 오피스까지 서초구 특성에 맞춘 출장 동선으로 운영합니다.",
        "강남 인접 서초 일대 고급 주거·오피스에서 프리미엄 코스 문의가 많습니다.",
    ],
    "seoul-yongsan": [
        "이태원·한남·용산역 인근 호텔·오피스텔, 청파·원효로 주거지까지 용산 특유의 국제·주거 혼합 지역에 맞춰 방문합니다.",
        "용산역·이태원 숙박시설에서 외국인·출장객 대상 당일 예약이 잦습니다.",
    ],
    "seoul-gwangjin": [
        "건대·자양·구의·화양 일대 대학가·상권 오피스텔, 한강 인근 주거지까지 광진구 특성에 맞게 배정합니다.",
        "건대입구·뚝섬역 인근 원룸·오피스텔에서 학생·직장인 당일 출장 문의가 많습니다.",
    ],
    "seoul-gwanak": [
        "신림·봉천 대학가 원룸·고시촌, 서울대 인근 자택까지 관악구 특성에 맞춰 찾아갑니다.",
        "신림역·봉천동 주거 밀집 지역에서 가성비 코스 출장 문의가 집중됩니다.",
    ],
    "incheon-yeonsu": [
        "송도 국제도시 호텔·오피스텔, 연수·동춘·옥련 주거지까지 송도·연수 특성에 맞춰 신속 방문합니다.",
        "송도 센트럴파크 인근 비즈니스 호텔에서 출장·장기체류 고객 문의가 많습니다.",
    ],
    "incheon-seogu": [
        "청라 국제도시·검단 신도시·가정·루원 주거지 등 서구 광역 신도시 특성에 맞춰 배정합니다.",
        "청라 호수공원 인근 오피스텔과 검단 아파트 단지에서 당일 출장이 가능합니다.",
    ],
    "busan-haeundae": [
        "해운대 해수욕장·센텀시티 호텔, 마린시티·재송 오피스텔까지 부산 대표 관광·비즈니스 지역에 맞춰 방문합니다.",
        "해운대·우동 숙박시설에서 여행·출장 중 당일·야간 출장마사지 문의가 집중됩니다.",
    ],
    "busan-suyeong": [
        "광안리·민락·수영 해안가 호텔·펜션, 망미·남천 주거지까지 수영구 해안 특성에 맞춰 찾아갑니다.",
        "광안대교 뷰 숙소와 광안리 게스트하우스에서 관광객 예약이 많습니다.",
    ],
    "gyeonggi-seongnam": [
        "분당·판교·정자 IT 단지 오피스텔, 수정·중원 주거지까지 성남권 업무·주거 특성에 맞춰 배정합니다.",
        "판교 테크노밸리 인근 숙박·오피스에서 야근 후 출장 문의가 이어집니다.",
    ],
    "gyeonggi-goyang": [
        "일산·킨텍스·화정·행신·덕양 등 고양시 광역 주거지에 맞춰 동선을 나눠 신속 방문합니다.",
        "킨텍스 전시·행사 출장객과 일산 신도시 거주 고객 문의가 많습니다.",
    ],
    "gyeonggi-hwaseong": [
        "동탄 신도시·병점·향남·봉담 등 화성시 대규모 주거·산단 지역 특성에 맞춰 배정합니다.",
        "동탄역·동탄신도시 오피스텔에서 당일·야간 출장 예약이 집중됩니다.",
    ],
    "jeju-si": [
        "제주시 연동·노형·이도·애월 등 관광·주거 혼합 지역에 맞춰 호텔·펜션·자택으로 방문합니다.",
        "제주공항 인근 숙박시설과 연동 먹자골목 주변 호텔에서 여행 중 출장 문의가 많습니다.",
    ],
    "gyeonggi-paju": [
        "파주는 운정·교하 신도시와 금촌·문산 기존 생활권이 나뉘어 있어, 동네별 이동 시간 차이가 큽니다. 상담 시 운정·금촌·교하·문산 중 어디인지 알려주시면 배정과 도착 예상 시간을 맞춰 안내합니다.",
        "자택·오피스텔·숙박시설 모두 방문 가능하며, 경기 북부 특성상 저녁·주말 당일 예약 문의가 많습니다. 코스·시간은 전화·카톡으로 조율하세요.",
        "운정신도시·금촌역·교하·문산 일대는 업체마다 커버 범위가 다를 수 있으니, 아래 안내를 읽은 뒤 업체를 고르시면 더 수월합니다.",
    ],
}

STREET_HINTS: dict[str, str] = {
    "seoul-gangnam": "테헤란로·강남대로 일대",
    "seoul-mapo": "홍익로·합정역 일대",
    "seoul-songpa": "올림픽로·잠실역 일대",
    "seoul-jung": "을지로·명동길 일대",
    "incheon-yeonsu": "송도국제대로 일대",
    "busan-haeundae": "해운대해변로 일대",
    "gyeonggi-seongnam": "판교역로·분당 내곡 일대",
}


def _slug_hash(slug: str) -> int:
    return sum(ord(c) for c in slug)


def _dong_pair(area: dict) -> tuple[str, str, str]:
    dongs = area.get("dong") or ["전지역"]
    d1 = dongs[0]
    d2 = dongs[1] if len(dongs) > 1 else d1
    d3 = dongs[2] if len(dongs) > 2 else d1
    return d1, d2, d3


def _build_highlights(metro: dict, area: dict, slug: str) -> list[str]:
    if slug in HIGHLIGHTS:
        base = list(HIGHLIGHTS[slug])
    else:
        short = area.get("short", area["name"])
        name = area["name"]
        metro_name = metro["name"]
        d1, d2, d3 = _dong_pair(area)
        idx = _slug_hash(slug) % 5

        pools = [
            [
                f"{metro_name} {name} {d1}·{d2} 일대 호텔·오피스텔·자택으로 관리사가 직접 찾아갑니다. {short} 생활권 특성에 맞춰 배차해 대기 시간을 줄입니다.",
                f"{d3}·{d1} 인근 숙박·주거 단지에서 당일·야간 방문 문의가 많으며, 전화·카톡 상담 후 일정을 안내해 드립니다.",
            ],
            [
                f"{short} {d1} 거주지와 {d2} 상권 인근 오피스텔까지 {metro_name} {name} 전역 방문이 가능합니다. 샵 이동 없이 머무는 공간에서 케어를 받는 방문형 서비스입니다.",
                f"{d2}·{d3} 일대에서 퇴근 후·주말 당일 예약 문의가 이어지며, 코스·시간은 상담 시 맞춰 조율합니다.",
            ],
            [
                f"{name} {d1}·{d2}·{d3} 등 {short} 핵심 동네 호텔·펜션·자택 방문에 맞춰 운영합니다. {metro_name} 기준 신속 배정을 안내해 드립니다.",
                f"{short} 역세권·주거 단지에서 24시간 전화·카톡 상담 후 바디 릴렉스·스웨디시·시그니처 코스 중 선택할 수 있습니다.",
            ],
            [
                f"{metro_name} {short} {d1} 인근 비즈니스 호텔과 {d2} 주거지까지 출장 동선을 최적화합니다. 출장·재택·여행 중에도 이동 부담 없이 이용하세요.",
                f"{d3} 일대 장기체류·출장 고객과 지역 거주민 모두 {name} 전지역 상담이 가능합니다.",
            ],
            [
                f"{short} {d1}·{d3} 상권과 {d2} 주택가 등 {name} 생활권에 맞춰 관리사를 배정합니다. 지역별 이동 패턴을 반영해 방문 시간을 안내합니다.",
                f"{metro_name} {name} 호텔·오피스텔·자택 어디든 상담 가능하며, 컨디션에 맞는 코스를 추천해 드립니다.",
            ],
        ]
        base = pools[idx]

    short = area.get("short", area["name"])
    name = area["name"]
    metro_name = metro["name"]
    d1, d2, _ = _dong_pair(area)
    tidx = _slug_hash(slug + "t") % 4
    third_lines = [
        f"이 페이지는 {metro_name} {name}({short}) 전용 안내입니다. 업체 카드에서 {short} 배정 가능 업체·코스·가격을 비교한 뒤 상담하세요.",
        f"{short} {d1}·{d2} 키워드로 검색하셨다면, 아래 업체 목록과 지역 맞춤 안내를 함께 참고하시면 됩니다.",
        f"{name} 인근 호텔·오피스텔·자택 이용 고객은 상담 시 동·건물명을 알려주시면 {short} 기준 방문 시간을 더 정확히 안내합니다.",
        f"{metro_name} {short} 지역은 업체마다 커버 범위가 다를 수 있습니다. 카드의 지역·가격 정보를 확인하고 전화·카톡으로 최종 확인하세요.",
    ]
    if len(base) >= 3:
        return base[:3]
    return base + [third_lines[tidx]]


def _why_titles(short: str, region_label: str, slug: str) -> list[str]:
    pinned = {
        "seoul-gangnam": [
            f"1) {short} 호텔·자택에서 편하게 이용하는 출장마사지",
            f"2) {short} 당일·야간에도 가능한 24시 출장 예약",
            f"3) {region_label} 방문 후 결제하는 후불제 출장",
            f"4) {short} 피로 부위에 맞춘 맞춤 출장 코스",
        ],
    }
    if slug in pinned:
        return pinned[slug]
    idx = _slug_hash(slug) % 4
    sets = [
        [
            f"1) {short} 호텔·자택에서 편하게 이용하는 출장마사지",
            f"2) {short} 당일·야간에도 가능한 24시 출장 예약",
            f"3) {region_label} 방문 후 결제하는 후불제 출장",
            f"4) {short} 피로 부위에 맞춘 맞춤 출장 코스",
        ],
        [
            f"1) {short} 오피스텔·숙박시설로 찾아가는 출장마사지",
            f"2) {short} 퇴근 후·여행 중에도 되는 야간 출장",
            f"3) {region_label} 후불제로 안심하고 받는 출장 관리",
            f"4) {short} 건식·힐링·프리미엄 출장 코스 선택",
        ],
        [
            f"1) {region_label} 원하는 장소로 오는 방문형 출장마사지",
            f"2) {short} 전지역 24시 전화·카톡 즉시 상담",
            f"3) {short} 관리사 도착 후 결제하는 후불 출장",
            f"4) {region_label} 컨디션별 맞춤 출장 테라피",
        ],
        [
            f"1) {short} 역세권·주거지 호텔 출장마사지",
            f"2) {region_label} 당일 예약·빠른 배정 안내",
            f"3) {short} 선결제 없이 이용하는 후불 출장",
            f"4) {short} 부위·강도 맞춤 출장마사지 코스",
        ],
    ]
    return sets[idx]


def why_bodies(
    region_label: str, dong_list: str, count: int, slug: str
) -> list[str]:
    dong_hint = dong_list.replace("·", ", ") if dong_list else region_label
    idx = _slug_hash(slug) % 3
    bodies = [
        [
            f"{region_label} 호텔·펜션·자택·오피스텔로 관리사가 직접 방문합니다. 샵까지 이동할 필요 없이 편한 공간에서 케어를 받을 수 있습니다.",
            f"24시간 전화·카톡 상담으로 {region_label} 기준 빠른 배정이 가능합니다. 퇴근 후, 여행 중, 갑작스러운 피로가 쌓였을 때도 부담 없이 문의하세요.",
            "관리사 도착·코스 확인 후 결제하는 후불제로 운영됩니다. 현금·계좌이체·카드 등 결제 방법은 상담 시 안내해 드립니다.",
            f"바디 릴렉스·스웨디시·시그니처 등 원하시는 강도와 부위에 맞춰 코스를 안내합니다. {dong_hint} 등 {region_label} 전지역에서 이용하실 수 있습니다.",
        ],
        [
            f"{region_label} 머무시는 숙소·거주지로 찾아가는 방문형 출장입니다. 외출·대기 없이 제한된 시간을 효율적으로 쓸 수 있습니다.",
            f"{region_label} 기준 당일·심야 예약 가능 여부를 상담 시 바로 안내합니다. 급한 일정에도 전화·카톡으로 먼저 문의해 주세요.",
            "이용 전 선결제 없이 후불로 결제합니다. 코스·시간 확인 후 편한 방법으로 결제하시면 됩니다.",
            f"{dong_hint} 일대를 포함해 {region_label} 전역에서 피로·통증 부위에 맞는 코스를 추천해 드립니다.",
        ],
        [
            f"출장·여행·야근 후 {region_label} 호텔·오피스텔에서 그대로 이용할 수 있습니다. 이동 피로 없이 휴식과 동시에 관리를 받으세요.",
            "24시간 운영 상담으로 늦은 시간 예약도 가능합니다. 배정 상황에 따라 방문 시각을 안내해 드립니다.",
            f"{region_label} 전 지역 후불제 운영으로 안심하고 예약하실 수 있습니다. 결제 수단은 상담 시 확인하세요.",
            f"바디 릴렉스부터 스웨디시·시그니처 코스까지 {region_label}({dong_hint}) 상황에 맞게 선택할 수 있습니다.",
        ],
    ]
    return bodies[idx][:count]


SERVICE_TIPS: dict[str, list[tuple[str, str]]] = {
    "gyeonggi-paju": [
        (
            "운정·교하 신도시",
            "아파트 단지·오피스텔이 많아 주차·동호수 안내가 중요합니다. 예약 시 동·호수 대략 위치를 알려주시면 관리사 동선을 줄일 수 있습니다.",
        ),
        (
            "금촌·문산 생활권",
            "기존 도심과 신도시 사이 이동이 있어, 금촌역·문산 방향은 상담 시 ‘어느 쪽 생활권인지’를 먼저 말씀해 주세요.",
        ),
        (
            "당일 예약 팁",
            "평일 저녁·주말 오후는 배정이 빠르게 차는 편입니다. 원하는 시간이 있으면 가능한 한 일찍 전화·카톡으로 문의하세요.",
        ),
    ],
}

LOCAL_NOTES: dict[str, list[tuple[str, str]]] = {
    "gyeonggi-paju": [
        (
            "운정 신도시 이용",
            "운정 호수공원·롯데몰 인근 아파트에서 퇴근 후 당일 예약 문의가 많습니다. 주차 가능 여부를 미리 알려주시면 원활합니다.",
        ),
        (
            "금촌·교하 출장",
            "금촌역 주변 오피스·자택과 교하 신도시 오피스텔 모두 방문 가능합니다. 코스는 바디 릴렉스부터 스웨디시까지 상담으로 맞춥니다.",
        ),
    ],
    "seoul-gangnam": [
        (
            "테헤란로·삼성동",
            "호텔·오피스텔 밀집 지역은 야근 후 늦은 시간 문의가 많습니다. 카드에서 가격·코스를 비교한 뒤 바로 상담하세요.",
        ),
        (
            "역삼·논현·청담",
            "비즈니스·주거 혼합 지역이라 당일 배정이 빠른 편입니다. 원하는 코스명을 함께 알려주시면 안내가 수월합니다.",
        ),
    ],
}


def _auto_service_tips(
    metro: dict, area: dict, slug: str, region_label: str
) -> list[tuple[str, str]]:
    short = area.get("short", area["name"])
    d1, d2, d3 = _dong_pair(area)
    metro_name = metro["name"]
    return [
        (
            f"{d1}·{d2} 생활권",
            f"{metro_name} {short} {d1}·{d2} 일대 자택·오피스텔·숙박시설 방문이 가능합니다. 예약 시 동·건물 위치를 알려주시면 방문 시간 안내가 수월합니다.",
        ),
        (
            "당일·야간 예약",
            f"{region_label}는 평일 저녁·주말에 당일 문의가 많습니다. 원하는 시간이 있으면 가능한 한 일찍 전화·카톡으로 문의하세요.",
        ),
        (
            f"{d3}·{short} 방문 안내",
            f"{d3} 포함 {short} 전역 상담이 가능합니다. 업체마다 커버 범위가 다를 수 있어 카드·상담으로 최종 확인하세요.",
        ),
    ]


def _auto_local_notes(
    metro: dict, area: dict, slug: str, region_label: str
) -> list[tuple[str, str]]:
    short = area.get("short", area["name"])
    d1, d2, _ = _dong_pair(area)
    idx = _slug_hash(slug + "note") % 3
    pools = [
        [
            (
                f"{d1} 인근 이용",
                f"{d1} 주거·상권 인근에서 출장마사지 문의가 많습니다. 주차·동호수 안내를 함께 알려주시면 원활합니다.",
            ),
            (
                f"{d2}·{short} 출장",
                f"{d2} 일대 오피스텔·자택 모두 방문 가능합니다. 코스는 바디 릴렉스부터 스웨디시·시그니처까지 상담으로 맞춥니다.",
            ),
        ],
        [
            (
                f"{short} 호텔·숙박",
                f"{region_label} 호텔·펜션·게스트하우스 이용 고객 문의가 이어집니다. 체크인 장소를 미리 알려주세요.",
            ),
            (
                f"{d1}·{d2} 생활권",
                f"{d1}·{d2} 중심 생활권은 배정 동선을 나눠 안내합니다. 급한 일정은 전화 상담을 권장합니다.",
            ),
        ],
        [
            (
                f"{short} 첫 이용",
                f"{region_label} 첫 이용이시라면 아래 FAQ와 이용 절차를 먼저 확인한 뒤 업체를 고르시면 편합니다.",
            ),
            (
                f"{d2} 당일 예약",
                f"{d2} 인근은 퇴근 시간대 문의가 집중됩니다. 코스명과 희망 시간을 함께 알려주세요.",
            ),
        ],
    ]
    return pools[idx]


def get_area_content(
    slug: str,
    metro: dict,
    area: dict,
    region_label: str,
    dong_list: str = "",
    *,
    page_type: str = "default",
) -> AreaContent:
    short = area.get("short", area["name"])
    name = area["name"]
    metro_admin = metro["name"]
    t = metro.get("type", "")
    if t == "특별시":
        locality = f"{metro_admin}특별시 {name}"
    elif t == "광역시":
        locality = f"{metro_admin}광역시 {name}"
    elif t == "특별자치도":
        locality = f"{metro_admin}특별자치도 {name}"
    elif t == "도":
        locality = f"{metro_admin}도 {name}"
    else:
        locality = f"{metro_admin} {name}"

    parent_slug = area.get("parent")
    postal = POSTAL_CODES.get(slug) or (
        POSTAL_CODES.get(parent_slug, "00000") if parent_slug else "00000"
    )
    street = STREET_HINTS.get(
        slug, f"{short} {(_dong_pair(area)[0])}·{(_dong_pair(area)[1])} 일대"
    )

    titles = _why_titles(short, region_label, slug)
    pinned_why = {
        "gyeonggi-paju": [
            f"1) {short} 자택·오피스텔로 찾아오는 방문형 출장",
            f"2) 운정·금촌·교하·문산 생활권 맞춤 상담",
            f"3) {region_label} 후불제 — 이용 후 결제",
            f"4) {short} 피로·컨디션별 코스 추천",
        ],
    }
    if slug in pinned_why:
        titles = pinned_why[slug]

    tips = SERVICE_TIPS.get(slug)
    notes = LOCAL_NOTES.get(slug)
    if page_type == "service-guide":
        if not tips:
            tips = _auto_service_tips(metro, area, slug, region_label)
        if not notes:
            notes = _auto_local_notes(metro, area, slug, region_label)

    return AreaContent(
        highlights=_build_highlights(metro, area, slug),
        why_titles=titles,
        postal_code=postal,
        address_locality=locality,
        street_address=street,
        course_prefix=short,
        service_tips=tips,
        local_notes=notes,
    )


def course_heading(prefix: str, key: str, course_name: str, slug: str) -> str:
    """가격표 H3 — 지역 키워드 + 코스명 변주"""
    labels = {
        "A": [
            f"{prefix} 바디 릴렉스 출장",
            f"{prefix} 지역 스트레칭·건식 출장",
            f"{prefix} 라이트 바디케어 출장",
        ],
        "B": [
            f"{prefix} 스웨디시·아로마 출장",
            f"{prefix} 감성 힐링 출장 코스",
            f"{prefix} 스탠다드 힐링 출장",
        ],
        "C": [
            f"{prefix} VIP 시그니처 출장",
            f"{prefix} 시그니처 프리미엄 출장",
            f"{prefix} 특급 시그니처 출장 코스",
        ],
    }
    idx = _slug_hash(slug + key) % 3
    return f"{labels[key][idx]} — {course_name}"
