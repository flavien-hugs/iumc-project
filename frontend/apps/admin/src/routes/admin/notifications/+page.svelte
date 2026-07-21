<script lang="ts">
	import { Bell } from 'phosphor-svelte';
	import { goto, invalidateAll } from '$app/navigation';
	import { apiCall } from '@iumc/api';
	import Pagination from '@iumc/ui/composants/Pagination.svelte';
	import { formatDateTime } from '$lib/labels';
	import type { NotificationRow } from './+page';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const notificationsPage = $derived(data.notificationsPage);

	async function markAllRead() {
		await apiCall('/admin/notifications/mark-read', { method: 'POST' });
		await invalidateAll();
	}

	async function openItem(item: NotificationRow) {
		const href = linkFor(item.resource, item.resource_id);
		if (!item.is_read) {
			await apiCall(`/admin/notifications/${item.id}/mark-read`, { method: 'POST' });
			await invalidateAll();
		}
		if (href) goto(href);
	}

	function linkFor(resource: string | null, resourceId: number | null): string | null {
		if (resource === 'service_request' && resourceId) return `/admin/requests/${resourceId}`;
		return null;
	}

	function changePage(nextPage: number) {
		goto(`/admin/notifications?page=${nextPage}`, { keepFocus: true });
	}
</script>

<svelte:head>
	<title>Notifications, panel IUMC</title>
</svelte:head>

<div class="flex flex-wrap items-center justify-between gap-4">
	<div>
		<h1 class="text-3xl font-semibold text-ink-950">Notifications</h1>
		<p class="mt-2 text-sm text-ink-800/70">
			{notificationsPage.unread_count} non lue{notificationsPage.unread_count > 1 ? 's' : ''}
		</p>
	</div>
	{#if notificationsPage.unread_count > 0}
		<button
			type="button"
			onclick={markAllRead}
			class="rounded-pill border border-ink-900/20 px-4 py-2 text-sm font-medium text-ink-900 hover:border-ink-900/40"
		>
			Tout marquer comme lu
		</button>
	{/if}
</div>

{#if notificationsPage.items.length === 0}
	<div class="mt-8 flex flex-col items-center gap-3 rounded-card border border-ink-900/10 bg-paper-50 px-6 py-16 text-center">
		<Bell size={32} class="text-ink-800/30" />
		<p class="font-medium text-ink-950">Aucune notification</p>
	</div>
{:else}
	<ul class="mt-8 space-y-2">
		{#each notificationsPage.items as item (item.id)}
			<li
				class={`rounded-card border border-ink-900/10 bg-paper-50 px-4 py-3 ${item.is_read ? 'opacity-60' : ''}`}
			>
				<button type="button" onclick={() => openItem(item)} class="flex w-full items-center gap-3 text-left">
					{#if !item.is_read}
						<span class="h-2 w-2 shrink-0 rounded-full bg-gold-500" aria-label="Non lue"></span>
					{/if}
					<div class="min-w-0 flex-1">
						<p class="truncate text-sm font-medium text-ink-950">{item.title}</p>
						<p class="text-xs text-ink-800/50">{formatDateTime(item.created_at)}</p>
					</div>
				</button>
			</li>
		{/each}
	</ul>

	<Pagination
		page={notificationsPage.page}
		pageSize={notificationsPage.page_size}
		total={notificationsPage.total}
		onchange={changePage}
	/>
{/if}
