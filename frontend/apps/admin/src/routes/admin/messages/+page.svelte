<script lang="ts">
	import { ChatText } from 'phosphor-svelte';
	import { goto, invalidateAll } from '$app/navigation';
	import { apiCall } from '@iumc/api';
	import Pagination from '@iumc/ui/composants/Pagination.svelte';
	import { formatDateTime } from '$lib/labels';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const messagesPage = $derived(data.messagesPage);

	async function toggleProcessed(id: number, isProcessed: boolean) {
		await apiCall(`/admin/contact-messages/${id}`, {
			method: 'PATCH',
			body: { is_processed: !isProcessed }
		});
		await invalidateAll();
	}

	function changePage(nextPage: number) {
		goto(`/admin/messages?page=${nextPage}`, { keepFocus: true });
	}
</script>

<svelte:head>
	<title>Messages, panel IUMC</title>
</svelte:head>

<h1 class="text-3xl font-semibold text-ink-950">Messages de contact</h1>
<p class="mt-2 text-sm text-ink-800/70">Messages reçus via le formulaire de contact du site.</p>

{#if messagesPage.items.length === 0}
	<div
		class="mt-8 flex flex-col items-center gap-3 rounded-card border border-ink-900/10 bg-paper-50 px-6 py-16 text-center"
	>
		<ChatText size={32} class="text-ink-800/30" />
		<p class="font-medium text-ink-950">Aucun message pour le moment</p>
	</div>
{:else}
	<div class="mt-8 space-y-4">
		{#each messagesPage.items as item (item.id)}
			<article
				class={`rounded-card border border-ink-900/10 bg-paper-50 p-5 ${item.is_processed ? 'opacity-60' : ''}`}
			>
				<div class="flex flex-wrap items-start justify-between gap-3">
					<div>
						<h2 class="font-semibold text-ink-950">{item.subject}</h2>
						<p class="text-xs text-ink-800/60">
							{item.name} · {item.phone}{item.email ? ` · ${item.email}` : ''} ·
							{formatDateTime(item.created_at)}
						</p>
					</div>
					<button
						type="button"
						onclick={() => toggleProcessed(item.id, item.is_processed)}
						class={`rounded-pill px-3 py-1 text-xs font-medium ${
							item.is_processed
								? 'bg-ink-900/5 text-ink-800/60 hover:bg-ink-900/10'
								: 'bg-gold-500 text-ink-950 hover:bg-gold-600'
						}`}
					>
						{item.is_processed ? 'Traité' : 'Marquer traité'}
					</button>
				</div>
				<p class="mt-3 text-sm whitespace-pre-line text-ink-800/85">{item.message}</p>
			</article>
		{/each}
	</div>

	<Pagination
		page={messagesPage.page}
		pageSize={messagesPage.page_size}
		total={messagesPage.total}
		onchange={changePage}
	/>
{/if}
