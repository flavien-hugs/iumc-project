<script lang="ts">
	import { ArrowRight } from 'phosphor-svelte';
	import { divisionIcon } from '$lib/content';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const division = $derived(data.division);
	const Icon = $derived(divisionIcon(division.slug));
</script>

<svelte:head>
	<title>{division.name}, IUMC</title>
	<meta name="description" content={division.short_description} />
</svelte:head>

<section class="mx-auto grid max-w-7xl items-start gap-12 px-6 pt-16 pb-16 md:grid-cols-2 lg:px-10">
	<div>
		<Icon class="h-12 w-12 text-ink-900" />
		<h1 class="mt-4 text-4xl font-semibold text-ink-950">{division.name}</h1>
		<p class="mt-4 max-w-[52ch] text-ink-800/80">{division.full_description}</p>
		<a
			href="/fr/demande"
			class="mt-6 inline-flex items-center gap-2 rounded-pill bg-gold-500 px-6 py-3 text-sm font-medium text-ink-950 transition-transform hover:bg-gold-600 active:scale-[0.98]"
		>
			Demander un accompagnement
			<ArrowRight size={16} />
		</a>
	</div>

	<div class="relative overflow-hidden rounded-card bg-ink-950 p-8 text-paper-50">
		<Icon class="pointer-events-none absolute -top-10 -right-10 h-56 w-56 text-paper-50/6" />
		<p class="text-xs font-medium tracking-wide text-paper-100/50 uppercase">
			Services du pôle
		</p>
		<ul class="mt-4 divide-y divide-paper-100/10">
			{#each division.services as service (service.slug)}
				<li>
					<a
						href={`/fr/services/${division.slug}/${service.slug}`}
						class="group flex items-center justify-between gap-4 py-3 text-sm text-paper-100/85 hover:text-gold-500"
					>
						{service.title}
						<ArrowRight
							size={14}
							class="shrink-0 opacity-0 transition-opacity group-hover:opacity-100"
						/>
					</a>
				</li>
			{/each}
		</ul>
	</div>
</section>
