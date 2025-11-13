<template>
  <div class="min-h-screen bg-gray-50">
    <main class="container mx-auto max-w-7xl px-4 py-8 space-y-8">
      <section
        v-if="isLoadingDashboard"
        class="flex h-72 items-center justify-center rounded-2xl border border-dashed border-purple-200 bg-white text-purple-600"
      >
        <div class="space-y-2 text-center">
          <p class="text-sm font-semibold uppercase tracking-wide">Loading</p>
          <p class="text-base">멘토 대시보드 데이터를 불러오는 중입니다…</p>
        </div>
      </section>

      <section
        v-else-if="loadError"
        class="space-y-8"
      >
        <!-- 통계 카드 -->
        <article class="space-y-6 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm lg:p-8">
          <header class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p class="text-sm font-semibold text-purple-600">멘토 대시보드</p>
              <h1 class="text-2xl font-semibold text-gray-900">안녕하세요, {{ mentorName }}님</h1>
              <p class="text-sm text-gray-500">이번 달 활동 현황을 한눈에 확인해보세요.</p>
            </div>
            <div class="rounded-xl bg-gradient-to-r from-purple-50 to-blue-50 px-4 py-3 text-sm text-purple-600">
              <span class="font-semibold">0%</span> 목표 달성률 ·
              <span class="font-semibold">0건</span> 신청 처리
            </div>
          </header>
          <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <article v-for="stat in [
              {icon: Calendar, label: '전체 신청', value: '0', color: 'bg-blue-100 text-blue-600'},
              {icon: Clock, label: '응답 대기', value: '0', color: 'bg-yellow-100 text-yellow-600'},
              {icon: Wallet, label: '확정된 세션', value: '0', color: 'bg-green-100 text-green-600'},
              {icon: Users, label: '고유 멘티', value: '0', color: 'bg-purple-100 text-purple-600'}
            ]" :key="stat.label" class="flex items-center justify-between rounded-2xl border border-gray-100 p-5 shadow-sm">
              <div>
                <p class="text-sm text-gray-500">{{ stat.label }}</p>
                <p class="mt-2 text-2xl font-semibold text-gray-900">{{ stat.value }}</p>
              </div>
              <div class="flex h-12 w-12 items-center justify-center rounded-xl" :class="stat.color">
                <component :is="stat.icon" class="h-6 w-6" />
              </div>
            </article>
          </div>
        </article>

        <!-- 커피챗 카드 -->
        <div class="grid gap-8 lg:grid-cols-[2fr_1fr]">
          <article class="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm lg:p-8">
            <div class="mb-6 flex items-center justify-between">
              <div>
                <h2 class="text-xl font-semibold text-gray-900">다가오는 커피챗</h2>
                <p class="text-sm text-gray-500">확정 및 응답 대기 중인 일정입니다.</p>
              </div>
              <span class="rounded-full bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-600">
                총 0건
              </span>
            </div>
            <div class="rounded-xl border border-dashed border-gray-300 bg-gray-50 p-10 text-center text-sm text-gray-500">
              <p class="font-semibold text-lg text-gray-700 mb-2">예정된 커피챗이 없습니다</p>
              <p class="mb-1">아직 신청받은 커피챗 내역이 없습니다.</p>
              <p class="mb-1">멘티가 신청하면 이곳에 표시됩니다.</p>
              <p class="text-xs text-gray-400">데이터가 없을 때는 이 안내가 보입니다.</p>
            </div>
          </article>
          <!-- 뱃지/레벨 카드 -->
          <article class="space-y-6 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm lg:p-8">
            <div class="flex items-start justify-between">
              <div>
                <h2 class="text-xl font-semibold text-gray-900">멘토 레벨</h2>
                <p class="text-sm text-gray-500">활동 기반 XP와 배지를 확인하세요.</p>
              </div>
              <span class="rounded-full bg-purple-50 px-4 py-1 text-sm font-semibold text-purple-600">Lv. 1</span>
            </div>
            <div>
              <p class="text-3xl font-semibold text-gray-900">0<span class="text-base font-medium text-gray-500"> P</span></p>
              <p class="text-sm text-gray-500">이번 주 XP 0</p>
            </div>
            <div>
              <div class="flex items-center justify-between text-xs text-gray-500">
                <span>다음 레벨까지</span>
                <span>0 / 500 XP</span>
              </div>
              <div class="mt-2 h-2 w-full rounded-full bg-gray-200">
                <div class="h-2 rounded-full bg-purple-500 transition-all" style="width: 0%"></div>
              </div>
            </div>
            <div>
              <h3 class="text-sm font-semibold text-gray-700">획득한 배지 (0 / 5)</h3>
              <div class="mt-3 grid grid-cols-2 gap-3">
                <div class="flex items-center gap-2 rounded-xl border p-3 border-gray-200 bg-gray-50 text-gray-400">
                  <Trophy class="h-5 w-5 text-blue-600" />
                  <span class="text-sm font-medium">첫 수락</span>
                </div>
                <div class="flex items-center gap-2 rounded-xl border p-3 border-gray-200 bg-gray-50 text-gray-400">
                  <Star class="h-5 w-5 text-yellow-500" />
                  <span class="text-sm font-medium">완료 전문가</span>
                </div>
                <div class="flex items-center gap-2 rounded-xl border p-3 border-gray-200 bg-gray-50 text-gray-400">
                  <Zap class="h-5 w-5 text-purple-500" />
                  <span class="text-sm font-medium">빠른 응답</span>
                </div>
                <div class="flex items-center gap-2 rounded-xl border p-3 border-gray-200 bg-gray-50 text-gray-400">
                  <Award class="h-5 w-5 text-green-600" />
                  <span class="text-sm font-medium">10회 달성</span>
                </div>
                <div class="flex items-center gap-2 rounded-xl border p-3 border-gray-200 bg-gray-50 text-gray-400">
                  <Crown class="h-5 w-5 text-orange-500" />
                  <span class="text-sm font-medium">20회 달성</span>
                </div>
              </div>
            </div>
            <div class="rounded-xl bg-gray-50 p-4">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-xs text-gray-500">내 순위</p>
                  <p class="text-lg font-semibold text-gray-900">데이터 없음</p>
                  <p class="text-xs text-gray-500">포인트 0</p>
                </div>
                <div class="flex items-center gap-2 text-gray-400">
                  <TrendingUp class="h-4 w-4" />
                  <span class="text-sm font-medium">변동 없음</span>
                </div>
              </div>
            </div>
          </article>
        </div>

        <!-- 리뷰 카드 -->
        <div class="grid gap-8 lg:grid-cols-[3fr_2fr]">
          <article class="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm lg:p-8">
            <div class="mb-6 flex items-center justify-between">
              <div>
                <h2 class="text-xl font-semibold text-gray-900">최근 받은 리뷰</h2>
                <p class="text-sm text-gray-500">멘티 피드백을 확인하세요.</p>
              </div>
              <div class="flex items-center gap-2 text-yellow-500">
                <Star class="h-5 w-5 fill-yellow-500" />
                <span class="text-2xl font-semibold text-gray-900">N/A</span>
              </div>
            </div>
            <div class="rounded-xl border border-dashed border-gray-300 bg-gray-50 p-10 text-center text-sm text-gray-500">
              아직 리뷰가 없습니다. 커피챗이 완료되면 멘티에게 후기를 요청해보세요.
            </div>
          </article>
          <!-- 인사이트 카드 -->
          <article class="rounded-2xl border border-gray-100 bg-gradient-to-br from-blue-600 to-purple-600 p-6 text-white shadow-lg lg:p-8">
            <h2 class="text-xl font-semibold">이번 주 인사이트</h2>
            <p class="mt-1 text-sm text-white/80">데이터 기반 핵심 지표</p>
            <div class="mt-6 space-y-4">
              <div class="rounded-xl bg-white/10 p-4 backdrop-blur">
                <p class="text-sm text-white/80">응답 필요한 신청</p>
                <p class="mt-1 text-xl font-semibold">0건</p>
                <p class="mt-1 text-xs text-white/70">빠른 응답이 필요한 요청입니다.</p>
              </div>
              <div class="rounded-xl bg-white/10 p-4 backdrop-blur">
                <p class="text-sm text-white/80">확정된 세션</p>
                <p class="mt-1 text-xl font-semibold">0건</p>
                <p class="mt-1 text-xs text-white/70">멘티와 일정이 확정된 커피챗</p>
              </div>
              <div class="rounded-xl bg-white/10 p-4 backdrop-blur">
                <p class="text-sm text-white/80">완료된 세션</p>
                <p class="mt-1 text-xl font-semibold">0건</p>
                <p class="mt-1 text-xs text-white/70">후기 요청이 가능한 세션</p>
              </div>
            </div>
            <div class="mt-6 rounded-xl border border-white/20 bg-white/10 p-4 text-sm text-white/80">
              상위 10% 멘토는 평균 응답 시간을 <span class="font-semibold text-white">2시간 이내</span>로 유지하고 있어요.
            </div>
          </article>
        </div>

        <!-- 목표/랭킹 카드 -->
        <div class="grid gap-8 lg:grid-cols-2">
          <article class="space-y-6 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm lg:p-8">
            <div>
              <h2 class="text-xl font-semibold text-gray-900">이번 달 목표</h2>
              <p class="text-sm text-gray-500">목표 달성 진행률을 확인하세요.</p>
            </div>
            <div class="space-y-6">
              <div class="space-y-3">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3">
                    <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gray-100">
                      <Target class="h-6 w-6 text-blue-600" />
                    </div>
                    <div>
                      <p class="text-sm text-gray-500">이번 달 확정된 세션</p>
                      <p class="text-base font-semibold text-gray-900">
                        <span class="text-blue-600">0</span>
                        <span class="text-sm font-normal text-gray-400"> / 8 건</span>
                      </p>
                    </div>
                  </div>
                  <span class="text-sm font-semibold text-gray-500">0%</span>
                </div>
                <div class="h-2 w-full rounded-full bg-gray-200">
                  <div class="h-2 rounded-full bg-blue-600" style="width: 0%"></div>
                </div>
              </div>
              <div class="space-y-3">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3">
                    <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gray-100">
                      <Star class="h-6 w-6 text-green-600" />
                    </div>
                    <div>
                      <p class="text-sm text-gray-500">이번 달 완료된 세션</p>
                      <p class="text-base font-semibold text-gray-900">
                        <span class="text-green-600">0</span>
                        <span class="text-sm font-normal text-gray-400"> / 6 건</span>
                      </p>
                    </div>
                  </div>
                  <span class="text-sm font-semibold text-gray-500">0%</span>
                </div>
                <div class="h-2 w-full rounded-full bg-gray-200">
                  <div class="h-2 rounded-full bg-green-600" style="width: 0%"></div>
                </div>
              </div>
              <div class="space-y-3">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3">
                    <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gray-100">
                      <TrendingUp class="h-6 w-6 text-purple-600" />
                    </div>
                    <div>
                      <p class="text-sm text-gray-500">응답률</p>
                      <p class="text-base font-semibold text-gray-900">
                        <span class="text-purple-600">0</span>
                        <span class="text-sm font-normal text-gray-400"> / 90 %</span>
                      </p>
                    </div>
                  </div>
                  <span class="text-sm font-semibold text-gray-500">0%</span>
                </div>
                <div class="h-2 w-full rounded-full bg-gray-200">
                  <div class="h-2 rounded-full bg-purple-600" style="width: 0%"></div>
                </div>
              </div>
            </div>
            <div class="rounded-xl border border-gray-100 bg-gray-50 p-4">
              <div class="flex items-center justify-between text-sm text-gray-600">
                <span>전체 달성률</span>
                <span class="text-base font-semibold text-blue-600">0%</span>
              </div>
              <p class="mt-2 text-xs text-gray-500">이번 달 말까지 0일 남았습니다.</p>
            </div>
          </article>
          <!-- 랭킹 카드 -->
          <article class="space-y-6 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm lg:p-8">
            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-xl font-semibold text-gray-900">멘토 랭킹</h2>
                <p class="text-sm text-gray-500">이번 달 상위 멘토 현황</p>
              </div>
              <div class="rounded-full bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-600">
                상위 10위까지 1200P
              </div>
            </div>
            <div class="rounded-xl border border-dashed border-gray-300 bg-gray-50 p-6 text-center text-sm text-gray-500">
              상위 멘토 데이터가 아직 준비되지 않았습니다.
            </div>
          </article>
        </div>

        <!-- 빠른 실행 카드 -->
        <article class="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm lg:p-8">
          <div class="mb-6">
            <h2 class="text-xl font-semibold text-gray-900">빠른 실행</h2>
            <p class="text-sm text-gray-500">자주 사용하는 기능에 빠르게 접근하세요.</p>
          </div>
          <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <button
              v-for="action in [
                {icon: Calendar, label: '일정 관리', description: '가능한 시간 설정', color: 'bg-blue-100 text-blue-600'},
                {icon: MessageSquare, label: '메시지', description: '멘티 답변하기', badge: null, color: 'bg-purple-100 text-purple-600'},
                {icon: Bell, label: '알림 설정', description: '세션 알림 관리', color: 'bg-yellow-100 text-yellow-600'},
                {icon: DollarSign, label: '정산 확인', description: '수익 내역 보기', color: 'bg-green-100 text-green-600'},
                {icon: TrendingUp, label: '목표 설정', description: '이번 달 목표', color: 'bg-orange-100 text-orange-600'},
                {icon: Settings, label: '설정', description: '프로필 및 환경설정', color: 'bg-gray-100 text-gray-600'}
              ]"
              :key="action.label"
              type="button"
              class="relative flex h-full flex-col justify-between rounded-xl border border-gray-200 bg-white p-4 text-left transition-all hover:border-blue-300 hover:shadow-md"
            >
              <div class="flex h-12 w-12 items-center justify-center rounded-lg" :class="action.color">
                <component :is="action.icon" class="h-6 w-6" />
              </div>
              <div class="mt-4 space-y-1">
                <p class="text-sm font-semibold text-gray-900">{{ action.label }}</p>
                <p class="text-xs text-gray-500">{{ action.description }}</p>
              </div>
              <span
                v-if="action.badge"
                class="absolute right-3 top-3 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs font-semibold text-white"
              >
                {{ action.badge }}
              </span>
            </button>
          </div>
        </article>
      </section>

      <section v-else class="space-y-8">
        <article class="space-y-6 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm lg:p-8">
          <header class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p class="text-sm font-semibold text-purple-600">멘토 대시보드</p>
              <h1 class="text-2xl font-semibold text-gray-900">안녕하세요, {{ mentorName }}님</h1>
              <p class="text-sm text-gray-500">이번 달 활동 현황을 한눈에 확인해보세요.</p>
            </div>
            <div class="rounded-xl bg-gradient-to-r from-purple-50 to-blue-50 px-4 py-3 text-sm text-purple-600">
              <span class="font-semibold">{{ overallGoalProgress }}%</span> 목표 달성률 ·
              <span class="font-semibold">{{ formatNumber(totalRequests) }}건</span> 신청 처리
            </div>
          </header>

          <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <article
              v-for="(stat, index) in stats"
              :key="index"
              class="flex items-center justify-between rounded-2xl border border-gray-100 p-5 shadow-sm transition-shadow hover:shadow-md"
            >
              <div>
                <p class="text-sm text-gray-500">{{ stat.label }}</p>
                <p class="mt-2 text-2xl font-semibold text-gray-900">{{ stat.value }}</p>
              </div>
              <div class="flex h-12 w-12 items-center justify-center rounded-xl" :class="stat.color">
                <component :is="stat.icon" class="h-6 w-6" />
              </div>
            </article>
          </div>
        </article>

        <div class="grid gap-8 lg:grid-cols-[2fr_1fr]">
          <article class="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm lg:p-8">
            <div class="mb-6 flex items-center justify-between">
              <div>
                <h2 class="text-xl font-semibold text-gray-900">다가오는 커피챗</h2>
                <p class="text-sm text-gray-500">확정 및 응답 대기 중인 일정입니다.</p>
              </div>
              <span class="rounded-full bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-600">
                총 {{ formatNumber(upcomingSessions.length) }}건
              </span>
            </div>

            <div v-if="upcomingSessions.length" class="space-y-4">
              <article
                v-for="session in upcomingSessions"
                :key="session.id"
                class="rounded-xl border border-gray-200 p-4 transition-all hover:border-blue-300 hover:bg-blue-50/40"
              >
                <div class="flex items-start justify-between gap-3">
                  <div class="flex items-center gap-3">
                    <img
                      :src="session.avatar || fallbackAvatar"
                      :alt="`${session.mentee} 프로필 이미지`"
                      class="h-12 w-12 rounded-full object-cover"
                      loading="lazy"
                      @error="handleAvatarError"
                    />
                    <div>
                      <p class="text-base font-semibold text-gray-900">{{ session.mentee }}</p>
                      <p class="text-sm text-gray-500 line-clamp-2">{{ session.topic }}</p>
                    </div>
                  </div>
                  <span class="rounded-full px-3 py-1 text-xs font-semibold" :class="session.statusClass">
                    {{ session.statusLabel }}
                  </span>
                </div>

                <div class="mt-4 flex flex-wrap items-center gap-4 text-sm text-gray-600">
                  <span class="flex items-center gap-1">
                    <Calendar class="h-4 w-4" />
                    {{ session.dateLabel }}
                  </span>
                  <span class="flex items-center gap-1">
                    <Clock class="h-4 w-4" />
                    {{ session.timeLabel }}
                  </span>
                  <span
                    class="flex items-center gap-1"
                    :class="session.type === 'online' ? 'text-blue-600' : 'text-purple-600'"
                  >
                    <component :is="session.type === 'online' ? Video : MapPin" class="h-4 w-4" />
                    {{ session.type === 'online' ? '온라인' : session.location }}
                  </span>
                </div>

                <div v-if="session.status === 'pending'" class="mt-4 flex gap-2">
                  <button
                    type="button"
                    class="flex-1 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-blue-700"
                  >
                    승인
                  </button>
                  <button
                    type="button"
                    class="flex-1 rounded-lg border border-gray-200 px-4 py-2 text-sm font-semibold text-gray-700 transition-colors hover:bg-gray-100"
                  >
                    보류
                  </button>
                </div>
              </article>
            </div>

            <div
              v-else
              class="rounded-xl border border-dashed border-gray-300 bg-gray-50 p-10 text-center text-sm text-gray-500"
            >
              아직 예정된 커피챗이 없습니다. 새로운 신청이 들어오면 여기에서 확인할 수 있어요.
            </div>
          </article>

          <article class="space-y-6 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm lg:p-8">
            <div class="flex items-start justify-between">
              <div>
                <h2 class="text-xl font-semibold text-gray-900">멘토 레벨</h2>
                <p class="text-sm text-gray-500">활동 기반 XP와 배지를 확인하세요.</p>
              </div>
              <span class="rounded-full bg-purple-50 px-4 py-1 text-sm font-semibold text-purple-600">
                Lv. {{ gamification.level }}
              </span>
            </div>

            <div>
              <p class="text-3xl font-semibold text-gray-900">
                {{ formatNumber(gamification.totalPoints) }}<span class="text-base font-medium text-gray-500"> P</span>
              </p>
              <p class="text-sm text-gray-500">이번 주 XP {{ formatNumber(gamification.weeklyXP) }}</p>
            </div>

            <div>
              <div class="flex items-center justify-between text-xs text-gray-500">
                <span>다음 레벨까지</span>
                <span>{{ formatNumber(gamification.currentXP) }} / {{ formatNumber(gamification.nextLevelXP) }} XP</span>
              </div>
              <div class="mt-2 h-2 w-full rounded-full bg-gray-200">
                <div class="h-2 rounded-full bg-purple-500 transition-all" :style="{ width: `${levelProgress}%` }"></div>
              </div>
            </div>

            <div>
              <h3 class="text-sm font-semibold text-gray-700">
                획득한 배지 ({{ earnedBadgeCount }} / {{ gamification.badges.length }})
              </h3>
              <div class="mt-3 grid grid-cols-2 gap-3">
                <div
                  v-for="badge in gamification.badges"
                  :key="badge.name"
                  class="flex items-center gap-2 rounded-xl border p-3"
                  :class="badge.earned ? 'border-purple-200 bg-purple-50 text-purple-700' : 'border-gray-200 bg-gray-50 text-gray-400'"
                >
                  <component :is="badge.icon" class="h-5 w-5" :class="badge.iconColor" />
                  <span class="text-sm font-medium">{{ badge.name }}</span>
                </div>
              </div>
            </div>

            <div class="rounded-xl bg-gray-50 p-4">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-xs text-gray-500">내 순위</p>
                  <p class="text-lg font-semibold text-gray-900">{{ myRanking.rank ? `#${myRanking.rank}` : '데이터 없음' }}</p>
                  <p class="text-xs text-gray-500">포인트 {{ formatNumber(myRanking.points) }}</p>
                </div>
                <div class="flex items-center gap-2" :class="rankingTrend.class">
                  <component :is="rankingTrend.icon" class="h-4 w-4" />
                  <span class="text-sm font-medium">{{ rankingTrend.text }}</span>
                </div>
              </div>
            </div>
          </article>
        </div>

        <div class="grid gap-8 lg:grid-cols-[3fr_2fr]">
          <article class="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm lg:p-8">
            <div class="mb-6 flex items-center justify-between">
              <div>
                <h2 class="text-xl font-semibold text-gray-900">최근 받은 리뷰</h2>
                <p class="text-sm text-gray-500">멘티 피드백을 확인하세요.</p>
              </div>
              <div class="flex items-center gap-2 text-yellow-500">
                <Star class="h-5 w-5 fill-yellow-500" />
                <span class="text-2xl font-semibold text-gray-900">{{ averageRatingLabel }}</span>
              </div>
            </div>

            <div v-if="recentReviews.length" class="space-y-4">
              <article
                v-for="review in recentReviews"
                :key="review.id"
                class="rounded-xl border border-gray-200 bg-gray-50 p-4"
              >
                <div class="flex items-start gap-3">
                  <img
                    :src="review.avatar || fallbackAvatar"
                    :alt="`${review.mentee} 프로필 이미지`"
                    class="h-10 w-10 rounded-full object-cover"
                    loading="lazy"
                    @error="handleAvatarError"
                  />
                  <div class="flex-1">
                    <div class="flex items-center justify-between">
                      <div class="flex items-center gap-2 text-sm text-gray-500">
                        <span class="font-semibold text-gray-900">{{ review.mentee }}</span>
                        <span>·</span>
                        <span>{{ review.dateLabel }}</span>
                      </div>
                      <div class="flex items-center gap-1">
                        <Star
                          v-for="index in 5"
                          :key="index"
                          class="h-4 w-4"
                          :class="index <= review.rating ? 'text-yellow-500 fill-yellow-500' : 'text-gray-300'"
                        />
                      </div>
                    </div>
                    <p class="mt-1 text-sm font-medium text-gray-600">{{ review.session }}</p>
                    <p class="mt-2 text-sm leading-relaxed text-gray-700">{{ review.comment }}</p>
                  </div>
                </div>
              </article>
            </div>

            <div
              v-else
              class="rounded-xl border border-dashed border-gray-300 bg-gray-50 p-10 text-center text-sm text-gray-500"
            >
              아직 리뷰가 없습니다. 커피챗이 완료되면 멘티에게 후기를 요청해보세요.
            </div>
          </article>

          <article class="rounded-2xl border border-gray-100 bg-gradient-to-br from-blue-600 to-purple-600 p-6 text-white shadow-lg lg:p-8">
            <h2 class="text-xl font-semibold">이번 주 인사이트</h2>
            <p class="mt-1 text-sm text-white/80">데이터 기반 핵심 지표</p>

            <div class="mt-6 space-y-4">
              <div
                v-for="insight in insights"
                :key="insight.title"
                class="rounded-xl bg-white/10 p-4 backdrop-blur"
              >
                <p class="text-sm text-white/80">{{ insight.title }}</p>
                <p class="mt-1 text-xl font-semibold">{{ insight.value }}</p>
                <p v-if="insight.description" class="mt-1 text-xs text-white/70">{{ insight.description }}</p>
              </div>
            </div>

            <div class="mt-6 rounded-xl border border-white/20 bg-white/10 p-4 text-sm text-white/80">
              상위 10% 멘토는 평균 응답 시간을 <span class="font-semibold text-white">2시간 이내</span>로 유지하고 있어요.
            </div>
          </article>
        </div>

        <div class="grid gap-8 lg:grid-cols-2">
          <article class="space-y-6 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm lg:p-8">
            <div>
              <h2 class="text-xl font-semibold text-gray-900">이번 달 목표</h2>
              <p class="text-sm text-gray-500">목표 달성 진행률을 확인하세요.</p>
            </div>

            <div class="space-y-6">
              <div v-for="goal in goals" :key="goal.title" class="space-y-3">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3">
                    <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gray-100">
                      <component :is="goal.icon" class="h-6 w-6" :class="goal.iconColor" />
                    </div>
                    <div>
                      <p class="text-sm text-gray-500">{{ goal.title }}</p>
                      <p class="text-base font-semibold text-gray-900">
                        <span :class="goal.valueColor">
                          {{ goal.unit === '원' ? formatCurrency(goal.current) : formatNumber(goal.current) }}
                        </span>
                        <span class="text-sm font-normal text-gray-400">
                          / {{ goal.unit === '원' ? formatCurrency(goal.target) : formatNumber(goal.target) }} {{ goal.unit }}
                        </span>
                      </p>
                    </div>
                  </div>
                  <span
                    class="text-sm font-semibold"
                    :class="goalProgressPercentage(goal) >= 100 ? 'text-green-600' : 'text-gray-500'"
                  >
                    {{ Math.round(Math.min(goalProgressPercentage(goal), 100)) }}%
                  </span>
                </div>
                <div class="h-2 w-full rounded-full bg-gray-200">
                  <div
                    class="h-2 rounded-full"
                    :class="goal.barColor"
                    :style="{ width: `${Math.min(goalProgressPercentage(goal), 100)}%` }"
                  ></div>
                </div>
                <p v-if="goal.achieved" class="text-xs font-semibold text-green-600">✓ 목표 달성!</p>
              </div>
            </div>

            <div class="rounded-xl border border-gray-100 bg-gray-50 p-4">
              <div class="flex items-center justify-between text-sm text-gray-600">
                <span>전체 달성률</span>
                <span class="text-base font-semibold text-blue-600">{{ overallGoalProgress }}%</span>
              </div>
              <p class="mt-2 text-xs text-gray-500">이번 달 말까지 {{ daysRemaining }}일 남았습니다.</p>
            </div>
          </article>

          <article class="space-y-6 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm lg:p-8">
            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-xl font-semibold text-gray-900">멘토 랭킹</h2>
                <p class="text-sm text-gray-500">이번 달 상위 멘토 현황</p>
              </div>
              <div class="rounded-full bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-600">
                상위 10위까지 {{ formatNumber(pointsToTopTen) }}P
              </div>
            </div>

            <div class="rounded-xl border border-blue-100 bg-gradient-to-r from-blue-50 to-purple-50 p-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div class="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-r from-blue-600 to-purple-600 text-lg font-semibold text-white">
                    {{ myRanking.rank ? `#${myRanking.rank}` : '-' }}
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">내 순위</p>
                    <p class="text-base font-semibold text-gray-900">{{ mentorName }}</p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="text-sm text-gray-500">포인트</p>
                  <p class="text-lg font-semibold text-blue-600">{{ formatNumber(myRanking.points) }}P</p>
                </div>
              </div>
            </div>

            <div v-if="topMentors.length" class="space-y-3">
              <article
                v-for="mentor in topMentors"
                :key="mentor.rank"
                class="flex items-center justify-between rounded-xl border border-gray-100 p-3"
              >
                <div class="flex items-center gap-3">
                  <div class="flex h-8 w-8 items-center justify-center text-sm font-semibold text-gray-500">
                    #{{ mentor.rank }}
                  </div>
                  <img
                    :src="mentor.avatar || fallbackAvatar"
                    :alt="`${mentor.name} 프로필 이미지`"
                    class="h-10 w-10 rounded-full object-cover"
                    loading="lazy"
                    @error="handleAvatarError"
                  />
                  <div>
                    <p class="text-sm font-semibold text-gray-900">{{ mentor.name }}</p>
                    <p class="text-xs text-gray-500">{{ mentor.category }}</p>
                  </div>
                </div>
                <p class="text-sm font-semibold text-gray-700">{{ formatNumber(mentor.points) }}P</p>
              </article>
            </div>

            <div
              v-else
              class="rounded-xl border border-dashed border-gray-300 bg-gray-50 p-6 text-center text-sm text-gray-500"
            >
              상위 멘토 데이터가 아직 준비되지 않았습니다.
            </div>
          </article>
        </div>

        <article class="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm lg:p-8">
          <div class="mb-6">
            <h2 class="text-xl font-semibold text-gray-900">빠른 실행</h2>
            <p class="text-sm text-gray-500">자주 사용하는 기능에 빠르게 접근하세요.</p>
          </div>

          <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <button
              v-for="action in quickActions"
              :key="action.label"
              type="button"
              class="relative flex h-full flex-col justify-between rounded-xl border border-gray-200 bg-white p-4 text-left transition-all hover:border-blue-300 hover:shadow-md"
            >
              <div class="flex h-12 w-12 items-center justify-center rounded-lg" :class="action.color">
                <component :is="action.icon" class="h-6 w-6" />
              </div>
              <div class="mt-4 space-y-1">
                <p class="text-sm font-semibold text-gray-900">{{ action.label }}</p>
                <p class="text-xs text-gray-500">{{ action.description }}</p>
              </div>
              <span
                v-if="action.badge"
                class="absolute right-3 top-3 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs font-semibold text-white"
              >
                {{ action.badge }}
              </span>
            </button>
          </div>
        </article>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import { useAuthStore } from '@/store/auth';
import api from '@/services/api';
import {
  Calendar,
  Clock,
  TrendingUp,
  TrendingDown,
  Wallet,
  Users,
  Star,
  Trophy,
  Target,
  Zap,
  Award,
  Crown,
  Video,
  MapPin,
  MessageSquare,
  Settings,
  Bell,
  DollarSign,
  Medal
} from 'lucide-vue-next';

const authStore = useAuthStore();
const mentorName = computed(() => authStore.userName || '멘토');

const isLoadingDashboard = ref(false);
const loadError = ref(null);
const bookings = ref([]);

const fetchMentorDashboard = async () => {
  if (authStore.userRole !== 'mentor') {
    bookings.value = [];
    return;
  }

  isLoadingDashboard.value = true;
  loadError.value = null;

  try {
    const response = await api.get('/bookings/received/me');
    // 404 또는 빈 배열일 때 안내 메시지 표시
    if (response.status === 404 || (Array.isArray(response.data) && response.data.length === 0)) {
      bookings.value = [];
      loadError.value = { message: '신청받은 커피챗 내역이 없습니다.' };
    } else {
      bookings.value = Array.isArray(response.data) ? response.data : [];
    }
  } catch (error) {
    console.error('멘토 대시보드 데이터 로딩 실패:', error);
    loadError.value = error;
    bookings.value = [];
  } finally {
    isLoadingDashboard.value = false;
  }
};

watch(
  () => authStore.userRole,
  (role) => {
    if (role === 'mentor') {
      fetchMentorDashboard();
    } else {
      bookings.value = [];
    }
  },
  { immediate: true }
);

const retryFetch = () => fetchMentorDashboard();

const errorMessage = computed(() => {
  if (!loadError.value) return '';
  // 안내 메시지(데이터 없음) 우선
  if (loadError.value.message === '신청받은 커피챗 내역이 없습니다.') {
    return '아직 신청받은 커피챗 내역이 없습니다. 멘티가 신청하면 이곳에 표시됩니다.';
  }
  return (
    loadError.value.response?.data?.detail ||
    loadError.value.message ||
    '알 수 없는 오류가 발생했습니다.'
  );
});

const normalizedStatus = (status) => (status || '').toString().toLowerCase();

const statusLabels = {
  pending: '대기중',
  waiting: '대기중',
  requested: '대기중',
  approved: '확정',
  confirmed: '확정',
  accepted: '확정',
  completed: '완료',
  done: '완료',
  finished: '완료',
  rejected: '거절',
  cancelled: '취소됨',
  canceled: '취소됨'
};

const statusClassMap = {
  pending: 'bg-yellow-100 text-yellow-700',
  waiting: 'bg-yellow-100 text-yellow-700',
  requested: 'bg-yellow-100 text-yellow-700',
  approved: 'bg-green-100 text-green-700',
  confirmed: 'bg-green-100 text-green-700',
  accepted: 'bg-green-100 text-green-700',
  completed: 'bg-blue-100 text-blue-700',
  done: 'bg-blue-100 text-blue-700',
  finished: 'bg-blue-100 text-blue-700',
  rejected: 'bg-red-100 text-red-600',
  cancelled: 'bg-gray-200 text-gray-600',
  canceled: 'bg-gray-200 text-gray-600'
};

const getFirstValue = (source, keys) => {
  if (!source) return null;
  for (const key of keys) {
    if (source[key] !== undefined && source[key] !== null && source[key] !== '') {
      return source[key];
    }
  }
  return null;
};

const parseToDate = (value) => {
  if (!value) return null;
  if (value instanceof Date) {
    return Number.isNaN(value.getTime()) ? null : value;
  }

  if (typeof value === 'string') {
    const trimmed = value.trim();
    if (!trimmed) return null;

    const isoCandidate = new Date(trimmed);
    if (!Number.isNaN(isoCandidate.getTime())) {
      return isoCandidate;
    }

    if (/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) {
      return new Date(`${trimmed}T00:00:00`);
    }
  }
  return null;
};

const formatDateLabel = (dateObj, fallback) => {
  if (dateObj) {
    return new Intl.DateTimeFormat('ko-KR', {
      month: 'long',
      day: 'numeric',
      weekday: 'short'
    }).format(dateObj);
  }
  if (typeof fallback === 'string' && fallback.trim()) {
    return fallback;
  }
  return '날짜 미정';
};

const formatTimeLabel = (timeValue) => {
  if (!timeValue) return '시간 미정';

  if (typeof timeValue === 'string') {
    const trimmed = timeValue.trim();
    if (/^\d{1,2}:\d{2}/.test(trimmed)) {
      return trimmed;
    }

    const parsed = new Date(trimmed);
    if (!Number.isNaN(parsed.getTime())) {
      return new Intl.DateTimeFormat('ko-KR', {
        hour: '2-digit',
        minute: '2-digit'
      }).format(parsed);
    }

    return trimmed;
  }

  if (timeValue instanceof Date && !Number.isNaN(timeValue.getTime())) {
    return new Intl.DateTimeFormat('ko-KR', {
      hour: '2-digit',
      minute: '2-digit'
    }).format(timeValue);
  }

  return '시간 미정';
};

const formatRelativeTime = (dateObj) => {
  if (!dateObj) return '날짜 미정';
  const diffMs = Date.now() - dateObj.getTime();
  if (diffMs < 0) return '방금 전';

  const diffMinutes = Math.floor(diffMs / 60000);
  if (diffMinutes < 1) return '방금 전';
  if (diffMinutes < 60) return `${diffMinutes}분 전`;

  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}시간 전`;

  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 30) return `${diffDays}일 전`;

  const diffMonths = Math.floor(diffDays / 30);
  if (diffMonths < 12) return `${diffMonths}개월 전`;

  const diffYears = Math.floor(diffDays / 365);
  return `${diffYears}년 전`;
};

const formatNumber = (value) => {
  if (typeof value !== 'number' || Number.isNaN(value)) return '0';
  return value.toLocaleString('ko-KR');
};

const formatCurrency = (value) => {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) {
    return '₩0';
  }
  return `₩${Math.round(numeric).toLocaleString('ko-KR')}`;
};

const candidateDateFields = [
  'scheduled_at',
  'scheduled_date',
  'meeting_date',
  'session_date',
  'preferred_date',
  'preferredDate',
  '희망날짜',
  'completed_at',
  'completedAt',
  'updated_at',
  'updatedAt',
  'created_at',
  'createdAt'
];

const candidateTimeFields = [
  'scheduled_time',
  'meeting_time',
  'session_time',
  'preferred_time',
  'preferredTime',
  '희망시간'
];

const topicFields = [
  'topic',
  'mentoring_topic',
  'mentee_topic',
  'subject',
  'title',
  '멘티요청',
  '멘티질문',
  'mentee_request',
  'menteeMessage'
];

const locationFields = [
  'location',
  'meeting_location',
  'preferred_location',
  'meeting_place',
  'address',
  '장소'
];

const ratingFields = ['rating', 'review_score', 'score', '별점'];
const commentFields = ['review_comment', 'comment', 'feedback', 'review', '멘티후기'];
const reviewDateFields = [
  'reviewed_at',
  'reviewedAt',
  'completed_at',
  'completedAt',
  'updated_at',
  'updatedAt',
  'created_at',
  'createdAt'
];

const avatarFields = [
  'mentee_avatar',
  'menteeAvatar',
  'mentee_avatar_url',
  'menteeAvatarUrl',
  'mentee_avatarUrl',
  'menteeAvatarURL',
  'avatar',
  'avatar_url',
  'avatarUrl',
  'profile_image',
  'profileImage'
];

const totalRequests = computed(() => bookings.value.length);

const pendingStatuses = ['pending', 'waiting', 'requested'];
const confirmedStatuses = ['approved', 'confirmed', 'accepted'];
const completedStatuses = ['completed', 'done', 'finished'];

const pendingCount = computed(
  () => bookings.value.filter((booking) => pendingStatuses.includes(normalizedStatus(booking.status))).length
);

const confirmedCount = computed(
  () => bookings.value.filter((booking) => confirmedStatuses.includes(normalizedStatus(booking.status))).length
);

const completedCount = computed(
  () => bookings.value.filter((booking) => completedStatuses.includes(normalizedStatus(booking.status))).length
);

const uniqueMenteesCount = computed(() => {
  const menteeIds = new Set();
  bookings.value.forEach((booking) => {
    const menteeId =
      booking.멘티id ||
      booking.mentee_id ||
      booking.menteeId ||
      booking.mentee?.id ||
      null;
    const menteeName = booking.mentee?.full_name || booking.mentee_name;
    if (menteeId) {
      menteeIds.add(menteeId);
    } else if (menteeName) {
      menteeIds.add(menteeName);
    }
  });
  return menteeIds.size;
});

const stats = computed(() => [
  {
    icon: Calendar,
    label: '전체 신청',
    value: formatNumber(totalRequests.value),
    color: 'bg-blue-100 text-blue-600'
  },
  {
    icon: Clock,
    label: '응답 대기',
    value: formatNumber(pendingCount.value),
    color: 'bg-yellow-100 text-yellow-600'
  },
  {
    icon: Wallet,
    label: '확정된 세션',
    value: formatNumber(confirmedCount.value),
    color: 'bg-green-100 text-green-600'
  },
  {
    icon: Users,
    label: '고유 멘티',
    value: formatNumber(uniqueMenteesCount.value),
    color: 'bg-purple-100 text-purple-600'
  }
]);

const extractDateForStats = (booking) => {
  const raw = getFirstValue(booking, candidateDateFields);
  return parseToDate(raw);
};

const bookingsThisMonth = computed(() => {
  const now = new Date();
  return bookings.value.filter((booking) => {
    const date = extractDateForStats(booking);
    return (
      date &&
      date.getFullYear() === now.getFullYear() &&
      date.getMonth() === now.getMonth()
    );
  });
});

const bookingsLastMonth = computed(() => {
  const now = new Date();
  const targetMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
  return bookings.value.filter((booking) => {
    const date = extractDateForStats(booking);
    return (
      date &&
      date.getFullYear() === targetMonth.getFullYear() &&
      date.getMonth() === targetMonth.getMonth()
    );
  });
});

const confirmedThisMonth = computed(() =>
  bookingsThisMonth.value.filter((booking) => confirmedStatuses.includes(normalizedStatus(booking.status))).length
);

const confirmedLastMonth = computed(() =>
  bookingsLastMonth.value.filter((booking) => confirmedStatuses.includes(normalizedStatus(booking.status))).length
);

const completedThisMonth = computed(() =>
  bookingsThisMonth.value.filter((booking) => completedStatuses.includes(normalizedStatus(booking.status))).length
);

const monthlyConfirmedTarget = 8;
const monthlyCompletedTarget = 6;

const goals = computed(() => [
  {
    icon: Target,
    title: '이번 달 확정된 세션',
    current: confirmedThisMonth.value,
    target: monthlyConfirmedTarget,
    unit: '건',
    iconColor: 'text-blue-600',
    valueColor: 'text-blue-600',
    barColor: 'bg-blue-600',
    achieved: confirmedThisMonth.value >= monthlyConfirmedTarget
  },
  {
    icon: Star,
    title: '이번 달 완료된 세션',
    current: completedThisMonth.value,
    target: monthlyCompletedTarget,
    unit: '건',
    iconColor: 'text-green-600',
    valueColor: 'text-green-600',
    barColor: 'bg-green-600',
    achieved: completedThisMonth.value >= monthlyCompletedTarget
  },
  {
    icon: TrendingUp,
    title: '응답률',
    current: totalRequests.value
      ? Number((((confirmedCount.value + completedCount.value) / totalRequests.value) * 100).toFixed(1))
      : 0,
    target: 90,
    unit: '%',
    iconColor: 'text-purple-600',
    valueColor: 'text-purple-600',
    barColor: 'bg-purple-600',
    achieved:
      totalRequests.value > 0 &&
      ((confirmedCount.value + completedCount.value) / totalRequests.value) * 100 >= 90
  }
]);

const goalProgressPercentage = (goal) => {
  if (goal.achieved) return 100;
  if (!goal.target) {
    return goal.current > 0 ? 100 : 0;
  }
  return (goal.current / goal.target) * 100;
};

const overallGoalProgress = computed(() => {
  if (!goals.value.length) return 0;
  const total = goals.value.reduce(
    (sum, goal) => sum + Math.min(goalProgressPercentage(goal), 100),
    0
  );
  return Math.round(total / goals.value.length);
});

const daysRemaining = computed(() => {
  const today = new Date();
  const endOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0);
  const diff = Math.ceil((endOfMonth - today) / (1000 * 60 * 60 * 24));
  return diff > 0 ? diff : 0;
});

const gamification = computed(() => {
  const totalPoints =
    confirmedCount.value * 80 +
    completedCount.value * 120 +
    pendingCount.value * 20;

  const level = Math.max(1, Math.floor(totalPoints / 500) + 1);
  const currentXP = totalPoints % 500;
  const nextLevelXP = 500;
  const weeklyXP = Math.min(totalPoints, 500);
  const completedAgainstTargets = monthlyConfirmedTarget + monthlyCompletedTarget || 1;
  const goalCompletion = Math.round(
    Math.min(
      100,
      ((confirmedThisMonth.value + completedThisMonth.value) / completedAgainstTargets) * 100
    )
  );

  return {
    level,
    totalPoints,
    currentXP,
    nextLevelXP,
    weeklyXP,
    ranking: Math.max(1, 50 - (confirmedCount.value + completedCount.value)),
    goalCompletion,
    badges: [
      { icon: Trophy, name: '첫 수락', iconColor: 'text-blue-600', earned: confirmedCount.value > 0 },
      { icon: Star, name: '완료 전문가', iconColor: 'text-yellow-500', earned: completedCount.value >= 5 },
      { icon: Zap, name: '빠른 응답', iconColor: 'text-purple-500', earned: pendingCount.value === 0 && totalRequests.value > 0 },
      { icon: Award, name: '10회 달성', iconColor: 'text-green-600', earned: confirmedCount.value >= 10 },
      { icon: Crown, name: '20회 달성', iconColor: 'text-orange-500', earned: confirmedCount.value >= 20 }
    ]
  };
});

const levelProgress = computed(() => {
  if (!gamification.value.nextLevelXP) return 0;
  return Math.min(100, (gamification.value.currentXP / gamification.value.nextLevelXP) * 100);
});

const earnedBadgeCount = computed(
  () => gamification.value.badges.filter((badge) => badge.earned).length
);

const fallbackAvatar = 'https://via.placeholder.com/96x96.png?text=Mentor';

const extractAvatar = (booking) => {
  const menteeAvatar = getFirstValue(booking.mentee || {}, [
    'avatar_url',
    'avatar',
    'profile_image',
    'profileImage',
    'image',
    'photo'
  ]);
  return menteeAvatar || getFirstValue(booking, avatarFields);
};

const extractSessionType = (booking) => {
  const rawType = getFirstValue(booking, ['meeting_type', 'type', 'meetingType', 'format']);
  if (typeof rawType === 'string') {
    const lowered = rawType.toLowerCase();
    if (lowered.includes('on')) return 'online';
    if (lowered.includes('off')) return 'offline';
  }
  if (booking.is_online) return 'online';
  if (booking.is_offline) return 'offline';
  return 'unknown';
};

const upcomingSessions = computed(() => {
  const relevantStatuses = new Set([...pendingStatuses, ...confirmedStatuses]);
  return bookings.value
    .filter((booking) => relevantStatuses.has(normalizedStatus(booking.status)))
    .map((booking) => {
      const rawDate = getFirstValue(booking, candidateDateFields);
      const rawTime = getFirstValue(booking, candidateTimeFields);
      const dateObj = parseToDate(rawDate) || parseToDate(rawTime);
      const timestamp = dateObj ? dateObj.getTime() : 0;

      const type = extractSessionType(booking);
      const location =
        type === 'online'
          ? '온라인'
          : getFirstValue(booking, locationFields) || '장소 협의 예정';

      const avatar = extractAvatar(booking);

      return {
        id: booking.id ?? booking.uuid ?? `booking-${timestamp}`,
        mentee: booking.mentee?.full_name || booking.mentee_name || '이름 없음',
        topic:
          getFirstValue(booking, topicFields) ||
          '상담 주제가 아직 등록되지 않았습니다.',
        status: normalizedStatus(booking.status),
        statusLabel:
          statusLabels[normalizedStatus(booking.status)] ||
          (booking.status || '상태 미정'),
        statusClass:
          statusClassMap[normalizedStatus(booking.status)] ||
          'bg-gray-100 text-gray-600',
        dateLabel: formatDateLabel(dateObj, rawDate),
        timeLabel: formatTimeLabel(rawTime),
        type,
        location,
        avatar,
        timestamp
      };
    })
    .sort((a, b) => a.timestamp - b.timestamp)
    .slice(0, 6);
});

const generateFallbackId = () => Math.random().toString(36).slice(2, 11);

const ratingsFromBookings = computed(() =>
  bookings.value
    .map((booking) => {
      const ratingValue = Number(getFirstValue(booking, ratingFields));
      if (!Number.isFinite(ratingValue)) return null;

      const comment =
        getFirstValue(booking, commentFields) ||
        '멘티가 아직 후기를 남기지 않았습니다.';
      const reviewDateRaw = getFirstValue(booking, reviewDateFields);
      const reviewDateObj = parseToDate(reviewDateRaw);
      const avatar = extractAvatar(booking);
      return {
        id: booking.id ?? generateFallbackId(),
        mentee: booking.mentee?.full_name || booking.mentee_name || '이름 없음',
        rating: ratingValue,
        comment,
        dateLabel: reviewDateObj ? formatRelativeTime(reviewDateObj) : (reviewDateRaw || '날짜 미정'),
        session:
          getFirstValue(booking, topicFields) || '커피챗',
        avatar
      };
    })
    .filter(Boolean)
);

const recentReviews = computed(() =>
  ratingsFromBookings.value.slice(0, 3)
);

const averageRating = computed(() => {
  if (!ratingsFromBookings.value.length) return null;
  const total = ratingsFromBookings.value.reduce(
    (sum, review) => sum + review.rating,
    0
  );
  return (total / ratingsFromBookings.value.length).toFixed(1);
});

const insights = computed(() => [
  {
    title: '응답 필요한 신청',
    value: `${formatNumber(pendingCount.value)}건`,
    description: '빠른 응답이 필요한 요청입니다.'
  },
  {
    title: '확정된 세션',
    value: `${formatNumber(confirmedCount.value)}건`,
    description: '멘티와 일정이 확정된 커피챗'
  },
  {
    title: '완료된 세션',
    value: `${formatNumber(completedCount.value)}건`,
    description: '후기 요청이 가능한 세션'
  }
]);

const myRanking = computed(() => {
  if (!totalRequests.value) {
    return { rank: 0, points: gamification.value.totalPoints, diff: 0 };
  }
  const estimatedRank = Math.max(1, 50 - (confirmedCount.value + completedCount.value));
  const diff = confirmedThisMonth.value - confirmedLastMonth.value;
  return {
    rank: estimatedRank,
    points: gamification.value.totalPoints,
    diff
  };
});

const rankingTrend = computed(() => {
  if (!totalRequests.value) {
    return { text: '데이터 없음', class: 'text-gray-400', icon: TrendingUp };
  }

  if (myRanking.value.diff > 0) {
    return { text: `+${myRanking.value.diff}`, class: 'text-green-600', icon: TrendingUp };
  }

  if (myRanking.value.diff < 0) {
    return { text: `${myRanking.value.diff}`, class: 'text-red-600', icon: TrendingDown };
  }

  return { text: '변동 없음', class: 'text-gray-500', icon: TrendingUp };
});

const topMentors = ref([]);

const pointsToTopTen = computed(() => {
  const gap = 1200 - gamification.value.totalPoints;
  return gap > 0 ? gap : 0;
});

const quickActions = computed(() => [
  {
    icon: Calendar,
    label: '일정 관리',
    description: '가능한 시간 설정',
    color: 'bg-blue-100 text-blue-600'
  },
  {
    icon: MessageSquare,
    label: '메시지',
    description: '멘티 답변하기',
    badge: pendingCount.value > 0 ? pendingCount.value : null,
    color: 'bg-purple-100 text-purple-600'
  },
  {
    icon: Bell,
    label: '알림 설정',
    description: '세션 알림 관리',
    color: 'bg-yellow-100 text-yellow-600'
  },
  {
    icon: DollarSign,
    label: '정산 확인',
    description: '수익 내역 보기',
    color: 'bg-green-100 text-green-600'
  },
  {
    icon: TrendingUp,
    label: '목표 설정',
    description: '이번 달 목표',
    color: 'bg-orange-100 text-orange-600'
  },
  {
    icon: Settings,
    label: '설정',
    description: '프로필 및 환경설정',
    color: 'bg-gray-100 text-gray-600'
  }
]);

const handleAvatarError = (event) => {
  if (event?.target && event.target.src !== fallbackAvatar) {
    event.target.src = fallbackAvatar;
  }
};

const averageRatingLabel = computed(() => averageRating.value ?? 'N/A');
</script>
