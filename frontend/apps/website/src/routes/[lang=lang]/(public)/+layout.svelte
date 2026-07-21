<script lang="ts">
	import SiteHeader from '$lib/components/SiteHeader.svelte';
	import SiteFooter from '$lib/components/SiteFooter.svelte';
	import WhatsAppButton from '$lib/components/WhatsAppButton.svelte';
	import type { Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();
</script>

<div class="flex min-h-[100dvh] flex-col">
	<SiteHeader />

	<main class="flex-1">
		{@render children()}
	</main>

	<SiteFooter />
</div>

<WhatsAppButton />
