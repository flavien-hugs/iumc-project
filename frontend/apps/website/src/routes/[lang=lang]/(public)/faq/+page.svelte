<script lang="ts">
	import { CaretDown } from 'phosphor-svelte';
	import Seo from '$lib/components/Seo.svelte';
	import SenufoFrieze from '@iumc/ui/illustrations/SenufoFrieze.svelte';
	import { reveal } from '$lib/actions/reveal';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
</script>

<Seo
	title="Foire aux questions, IUMC"
	description="Réponses aux questions courantes sur les services, les demandes et les rendez-vous chez IUMC."
/>

<section class="mx-auto max-w-3xl px-6 pt-16 pb-20 lg:px-10">
	<div use:reveal>
		<h1 class="text-4xl font-semibold text-ink-950 md:text-5xl">Foire aux questions</h1>
		<p class="mt-4 max-w-[55ch] text-ink-800/80">
			Les réponses aux questions les plus courantes. Pour toute autre demande, contactez IUMC
			directement.
		</p>
	</div>

	<SenufoFrieze class="mt-8 h-5 w-full text-gold-500/30" />

	<div class="mt-6 divide-y divide-ink-900/10 border-t border-ink-900/10">
		{#each data.faqs as item, i (item.question)}
			<details use:reveal={{ delay: i * 50 }} class="group py-2">
				<summary
					class="flex cursor-pointer list-none items-center justify-between gap-4 py-4 text-left font-medium text-ink-950 marker:content-none"
				>
					{item.question}
					<CaretDown
						size={18}
						class="shrink-0 text-ink-800/50 transition-transform group-open:rotate-180"
					/>
				</summary>
				<div class="iumc-rich-text pb-4 text-sm text-ink-800/75">{@html item.answer}</div>
			</details>
		{/each}
	</div>
</section>
