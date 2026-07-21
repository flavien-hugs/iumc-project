<script lang="ts">
	import {
		Article,
		Bell,
		CalendarBlank,
		CaretDoubleLeft,
		CaretDoubleRight,
		ChartBar,
		ChatText,
		ClockCounterClockwise,
		Envelope,
		Gear,
		Images,
		List,
		MapPinLine,
		Question,
		SignOut,
		Stack,
		Tray,
		Users
	} from 'phosphor-svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { apiCall, API_BASE } from '@iumc/api';
	import Drawer from '@iumc/ui/composants/Drawer.svelte';
	import { formatDateTime } from '$lib/labels';
	import type { Snippet } from 'svelte';
	import type { LayoutProps } from './$types';

	interface NotificationItem {
		id: number;
		type: string;
		title: string;
		resource: string | null;
		resource_id: number | null;
		is_read: boolean;
		created_at: string;
	}

	let { data, children }: LayoutProps & { children: Snippet } = $props();

	let unreadCount = $state(0);
	let mobileNavOpen = $state(false);
	let notificationsOpen = $state(false);
	let recentNotifications = $state<NotificationItem[]>([]);
	let recentLoading = $state(false);

	function notificationHref(item: NotificationItem): string | null {
		if (item.resource === 'service_request' && item.resource_id) {
			return `/admin/requests/${item.resource_id}`;
		}
		return null;
	}

	async function openNotifications() {
		mobileNavOpen = false;
		notificationsOpen = true;
		recentLoading = true;
		try {
			const result = await apiCall<{ items: NotificationItem[]; unread_count: number }>(
				'/admin/notifications?page=1&page_size=10'
			);
			recentNotifications = result.items;
			unreadCount = result.unread_count;
		} catch {
			// silencieux : la liste reste vide, pas bloquant
		} finally {
			recentLoading = false;
		}
	}

	async function markOneRead(item: NotificationItem) {
		if (item.is_read) return;
		item.is_read = true;
		unreadCount = Math.max(0, unreadCount - 1);
		try {
			await apiCall(`/admin/notifications/${item.id}/mark-read`, { method: 'POST' });
		} catch {
			// silencieux : resynchronisé à la prochaine ouverture
		}
	}

	async function markAllRead() {
		recentNotifications = recentNotifications.map((item) => ({ ...item, is_read: true }));
		unreadCount = 0;
		try {
			await apiCall('/admin/notifications/mark-read', { method: 'POST' });
		} catch {
			// silencieux : resynchronisé à la prochaine ouverture
		}
	}

	function openNotificationItem(item: NotificationItem) {
		markOneRead(item);
		const href = notificationHref(item);
		if (href) {
			notificationsOpen = false;
			goto(href);
		}
	}

	// Repliée : uniquement les icônes, avec infobulle au survol. Préférence
	// mémorisée pour ne pas la redemander à chaque session.
	let collapsed = $state(
		typeof localStorage !== 'undefined' && localStorage.getItem('iumc-sidebar-collapsed') === '1'
	);

	$effect(() => {
		localStorage.setItem('iumc-sidebar-collapsed', collapsed ? '1' : '0');
	});

	const role = $derived(data.user?.role ?? '');

	// Regroupement par catégories (PRD section 11).
	const groups = $derived([
		{
			label: 'Activité',
			items: [
				{ href: '/admin', label: 'Tableau de bord', icon: ChartBar, exact: true },
				// L'admin de contenu n'accède pas aux demandes (PRD section 12.2).
				...(role !== 'content_admin'
					? [
							{ href: '/admin/requests', label: 'Demandes', icon: Tray, exact: false },
							{ href: '/admin/appointments', label: 'Rendez-vous', icon: CalendarBlank, exact: false },
							{ href: '/admin/messages', label: 'Messages', icon: ChatText, exact: false }
						]
					: []),
				{ href: '/admin/notifications', label: 'Notifications', icon: Bell, exact: false, badge: true }
			]
		},
		{
			label: 'Contenus',
			items:
				role === 'super_admin' || role === 'content_admin'
					? [
							{ href: '/admin/content', label: 'Pôles & services', icon: Stack, exact: false },
							{ href: '/admin/locations', label: 'Implantations', icon: MapPinLine, exact: false },
							{ href: '/admin/articles', label: 'Articles', icon: Article, exact: false },
							{ href: '/admin/faq', label: 'FAQ', icon: Question, exact: false },
							{ href: '/admin/media', label: 'Médias', icon: Images, exact: false }
						]
					: []
		},
		{
			label: 'Administration',
			items:
				role === 'super_admin'
					? [
							{ href: '/admin/users', label: 'Utilisateurs', icon: Users, exact: false },
							{ href: '/admin/audit', label: "Journal d'activité", icon: ClockCounterClockwise, exact: false },
							{ href: '/admin/settings', label: 'Paramètres', icon: Gear, exact: false }
						]
					: []
		}
	]);

	function isActive(href: string, exact: boolean): boolean {
		return exact ? page.url.pathname === href : page.url.pathname.startsWith(href);
	}

	async function refreshUnread() {
		if (data.user === null) return;
		try {
			const result = await apiCall<{ unread_count: number }>('/admin/notifications');
			unreadCount = result.unread_count;
		} catch {
			// silencieux : le badge n'est pas critique
		}
	}

	// Rafraîchit le badge à chaque navigation (le layout persiste entre les
	// pages, un simple onMount raterait la connexion) ; les mises à jour en
	// direct sont ensuite poussées par le flux SSE ci-dessous (ADR-0016).
	$effect(() => {
		void page.url.pathname;
		refreshUnread();
	});

	// Flux temps réel (ADR-0016) : une notification créée pendant que le panel
	// est ouvert incrémente le badge et rejoint la liste récente, sans
	// attendre la prochaine navigation. Reconnexion automatique native
	// d'EventSource ; fermeture explicite au démontage.
	$effect(() => {
		if (!data.user) return;
		const source = new EventSource(`${API_BASE}/admin/notifications/stream`, {
			withCredentials: true
		});
		source.onmessage = (event) => {
			const item: NotificationItem = JSON.parse(event.data);
			unreadCount += 1;
			recentNotifications = [item, ...recentNotifications].slice(0, 10);
		};
		return () => source.close();
	});

	// Ferme le menu mobile à chaque changement de page.
	$effect(() => {
		void page.url.pathname;
		mobileNavOpen = false;
	});

	async function logout() {
		await apiCall('/auth/logout', { method: 'POST' });
		goto('/admin/login');
	}
</script>

{#snippet navList(iconOnly: boolean, theme: 'dark' | 'light', onNavigate?: () => void)}
	{@const colors =
		theme === 'dark'
			? {
					groupLabel: 'text-paper-100/40',
					divider: 'border-paper-100/10',
					inactive: 'text-paper-100/75 hover:bg-paper-50/5 hover:text-paper-50',
					active: 'bg-green-500/15 font-medium text-green-500'
				}
			: {
					groupLabel: 'text-ink-800/50',
					divider: 'border-ink-900/10',
					inactive: 'text-ink-800 hover:bg-ink-900/5 hover:text-ink-950',
					active: 'bg-green-500/15 font-medium text-green-600'
				}}
	{#each groups as group (group.label)}
		{#if group.items.length > 0}
			{#if iconOnly}
				<div class={`mx-3 my-2 border-t first:mt-0 ${colors.divider}`}></div>
			{:else}
				<p class={`mt-5 px-3 text-xs font-medium tracking-wide uppercase first:mt-0 ${colors.groupLabel}`}>
					{group.label}
				</p>
			{/if}
			{#each group.items as item (item.href)}
				{@const isNotifications = 'badge' in item && item.badge}
				{@const itemClass = `group relative flex w-full items-center rounded-input py-2.5 text-sm transition-colors ${iconOnly ? 'justify-center px-0' : 'gap-3 px-3'} ${
					isActive(item.href, item.exact) ? colors.active : colors.inactive
				}`}
				{#snippet itemContent()}
					<span class="relative">
						<item.icon size={18} />
						{#if isNotifications && unreadCount > 0 && iconOnly}
							<span class="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-green-500"></span>
						{/if}
					</span>
					{#if !iconOnly}
						<span class="flex-1 text-left">{item.label}</span>
						{#if isNotifications && unreadCount > 0}
							<span class="rounded-pill bg-green-500 px-2 py-0.5 text-xs font-semibold text-ink-950">
								{unreadCount}
							</span>
						{/if}
					{/if}
					{#if iconOnly}
						<span
							class="pointer-events-none absolute left-full z-20 ml-3 whitespace-nowrap rounded-input bg-ink-950 px-2.5 py-1.5 text-xs font-medium text-paper-50 opacity-0 shadow-lg transition-opacity group-hover:opacity-100"
						>
							{item.label}
						</span>
					{/if}
				{/snippet}
				{#if isNotifications}
					<button
						type="button"
						onclick={openNotifications}
						title={iconOnly ? item.label : undefined}
						class={itemClass}
					>
						{@render itemContent()}
					</button>
				{:else}
					<a href={item.href} onclick={onNavigate} title={iconOnly ? item.label : undefined} class={itemClass}>
						{@render itemContent()}
					</a>
				{/if}
			{/each}
		{/if}
	{/each}
{/snippet}

{#if data.user === null}
	{@render children()}
{:else}
	<div class="flex h-dvh overflow-hidden bg-paper-100">
		<!-- Rail desktop : défilement propre (nav) indépendant du contenu. -->
		<aside
			class={`hidden h-full shrink-0 flex-col bg-ink-950 text-paper-100 transition-[width] duration-200 md:flex ${collapsed ? 'w-[76px]' : 'w-64'}`}
		>
			<div class={`flex items-center px-4 py-6 ${collapsed ? 'justify-center' : 'justify-between'}`}>
				{#if !collapsed}
					<a href="/admin" class="font-display text-2xl font-semibold text-paper-50">
						IUMC
						<span class="block text-xs font-normal tracking-wide text-paper-100/50 uppercase">
							Panel d'administration
						</span>
					</a>
				{/if}
				<button
					type="button"
					onclick={() => (collapsed = !collapsed)}
					aria-label={collapsed ? 'Déployer le menu' : 'Réduire le menu'}
					class="rounded-input p-1.5 text-paper-100/60 hover:bg-paper-50/5 hover:text-paper-50"
				>
					{#if collapsed}
						<CaretDoubleRight size={18} />
					{:else}
						<CaretDoubleLeft size={18} />
					{/if}
				</button>
			</div>

			<nav
				class={`flex flex-1 flex-col gap-1 overflow-y-auto pb-4 ${collapsed ? 'px-3' : 'px-3'}`}
				aria-label="Navigation du panel"
			>
				{@render navList(collapsed, 'dark')}
			</nav>

			<div class={`border-t border-paper-100/10 py-4 ${collapsed ? 'px-2' : 'px-3'}`}>
				{#if !collapsed}
					<p class="truncate px-3 pb-2 text-xs text-paper-100/50">{data.user.name}</p>
				{/if}
				<button
					type="button"
					onclick={logout}
					title={collapsed ? 'Se déconnecter' : undefined}
					class={`group relative flex w-full items-center rounded-input py-2.5 text-sm text-paper-100/75 hover:bg-paper-50/5 hover:text-paper-50 ${collapsed ? 'justify-center' : 'gap-3 px-3'}`}
				>
					<SignOut size={18} />
					{#if !collapsed}
						Se déconnecter
					{:else}
						<span
							class="pointer-events-none absolute left-full z-20 ml-3 whitespace-nowrap rounded-input bg-ink-950 px-2.5 py-1.5 text-xs font-medium text-paper-50 opacity-0 shadow-lg transition-opacity group-hover:opacity-100"
						>
							Se déconnecter
						</span>
					{/if}
				</button>
			</div>
		</aside>

		<!-- Colonne de contenu : le bandeau mobile reste fixe, seul <main> défile. -->
		<div class="flex min-w-0 flex-1 flex-col overflow-hidden">
			<header
				class="flex h-14 shrink-0 items-center justify-between border-b border-ink-900/10 bg-paper-50 px-4 md:px-6"
			>
				<div class="flex items-center gap-2 md:hidden">
					<button
						type="button"
						onclick={() => (mobileNavOpen = true)}
						aria-label="Ouvrir le menu"
						class="p-2 text-ink-950"
					>
						<List size={22} />
					</button>
					<a href="/admin" class="font-display text-xl font-semibold text-ink-950">IUMC</a>
				</div>
				<span class="hidden md:block"></span>
				<div class="flex items-center gap-1">
					<button
						type="button"
						onclick={openNotifications}
						aria-label="Notifications"
						class="relative p-2 text-ink-800 hover:text-ink-950"
					>
						<Bell size={20} />
						{#if unreadCount > 0}
							<span class="absolute top-1 right-1 h-2 w-2 rounded-full bg-green-500"></span>
						{/if}
					</button>
					<button
						type="button"
						onclick={logout}
						aria-label="Se déconnecter"
						class="p-2 text-ink-800 hover:text-ink-950 md:hidden"
					>
						<SignOut size={20} />
					</button>
				</div>
			</header>

			<main class="flex-1 overflow-y-auto p-6 lg:p-10">
				{@render children()}
			</main>
		</div>
	</div>

	<Drawer
		open={mobileNavOpen}
		title="Navigation"
		side="left"
		width="sm"
		onclose={() => (mobileNavOpen = false)}
	>
		<nav class="flex flex-col gap-1" aria-label="Navigation du panel (mobile)">
			{@render navList(false, 'light', () => (mobileNavOpen = false))}
		</nav>
		<div class="mt-6 border-t border-ink-900/10 pt-4">
			<p class="truncate px-1 pb-2 text-xs text-ink-800/50">{data.user.name}</p>
			<button
				type="button"
				onclick={logout}
				class="flex w-full items-center gap-3 rounded-input px-1 py-2.5 text-sm text-ink-800 hover:text-ink-950"
			>
				<SignOut size={18} />
				Se déconnecter
			</button>
		</div>
	</Drawer>

	<Drawer
		open={notificationsOpen}
		title="Notifications"
		onclose={() => (notificationsOpen = false)}
	>
		<div class="flex flex-col gap-4">
			{#if unreadCount > 0}
				<button
					type="button"
					onclick={markAllRead}
					class="self-start text-sm font-medium text-ink-900 hover:text-green-600"
				>
					Tout marquer comme lu
				</button>
			{/if}

			{#if recentLoading}
				<p class="py-8 text-center text-sm text-ink-800/50">Chargement…</p>
			{:else if recentNotifications.length === 0}
				<p class="py-8 text-center text-sm text-ink-800/50">Aucune notification pour le moment.</p>
			{:else}
				<ul class="flex flex-col divide-y divide-ink-900/10">
					{#each recentNotifications as item (item.id)}
						<li>
							<button
								type="button"
								onclick={() => openNotificationItem(item)}
								class="flex w-full items-start gap-3 py-3 text-left hover:bg-ink-900/4"
							>
								<span
									class={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${item.is_read ? 'bg-transparent' : 'bg-green-500'}`}
								></span>
								<span class="flex-1">
									<span class={`block text-sm ${item.is_read ? 'text-ink-800/70' : 'font-medium text-ink-950'}`}>
										{item.title}
									</span>
									<span class="mt-0.5 block text-xs text-ink-800/50">
										{formatDateTime(item.created_at)}
									</span>
								</span>
							</button>
						</li>
					{/each}
				</ul>
			{/if}

			<a
				href="/admin/notifications"
				onclick={() => (notificationsOpen = false)}
				class="text-center text-sm font-medium text-ink-900 underline decoration-ink-900/30 underline-offset-4 hover:decoration-ink-900"
			>
				Voir toutes les notifications
			</a>
		</div>
	</Drawer>
{/if}
