<script lang="ts">
	import { ArrowRight } from 'phosphor-svelte';
	import { divisionIcon } from '$lib/content';
	import Seo from '$lib/components/Seo.svelte';
	import SenufoFrieze from '@iumc/ui/illustrations/SenufoFrieze.svelte';
	import { reveal } from '$lib/actions/reveal';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
</script>

<Seo
	title="Nos pôles d'activité, IUMC"
	description="Découvrez les pôles d'intervention d'IUMC : services juridiques, foncier et immobilier, agropastoral."
/>

<section class="mx-auto max-w-7xl px-6 pt-16 pb-8 lg:px-10" use:reveal>
	<h1 class="max-w-[20ch] text-4xl font-semibold text-ink-950 md:text-5xl">
		Nos pôles d'activité
	</h1>
	<p class="mt-4 max-w-[60ch] text-ink-800/80">
		Trois domaines d'intervention, pensés pour se compléter selon la nature de votre projet.
	</p>
</section>

<div class="mx-auto max-w-7xl px-6 lg:px-10">
	<SenufoFrieze class="h-5 w-full text-gold-500/30" />
</div>

{#each data.divisions as division, i (division.slug)}
	{@const Icon = divisionIcon(division.slug)}
	{@const reversed = i % 2 === 1}
	<section class={`relative overflow-hidden ${reversed ? 'bg-paper-100' : ''}`}>
		<Icon
			class={`pointer-events-none absolute -bottom-12 hidden h-56 w-56 text-ink-900/5 md:block ${reversed ? '-left-10 scale-x-[-1]' : '-right-10'}`}
		/>
		<div class="relative mx-auto max-w-7xl px-6 py-14 lg:px-10">
			<div class={`flex flex-col gap-10 md:items-start ${reversed ? 'md:flex-row-reverse' : 'md:flex-row'}`}>
				<div class="md:w-1/3" use:reveal>
					<span class="font-display text-sm tracking-[0.35em] text-green-500/60">
						{String(i + 1).padStart(2, '0')}
					</span>
					<Icon class="mt-3 h-10 w-10 text-ink-900" />
					<div class="mt-4 flex items-center gap-3">
						<h2 class="text-2xl font-semibold text-ink-950">{division.name}</h2>
						{#if division.status === 'coming_soon'}
							<span
								class="rounded-pill bg-cyan-600/10 px-3 py-1 text-xs font-medium text-cyan-600"
							>
								Bientôt disponible
							</span>
						{/if}
					</div>
					<p class="mt-3 text-sm text-ink-800/80">{division.full_description}</p>
					{#if division.status === 'active'}
						<a
							href={`/fr/services/${division.slug}`}
							class="mt-5 inline-flex items-center gap-2 text-sm font-medium text-ink-900 underline decoration-ink-900/30 underline-offset-4 hover:decoration-ink-900"
						>
							Voir le pôle
							<ArrowRight size={16} />
						</a>
					{/if}
				</div>

				<div class="md:w-2/3" use:reveal={{ delay: 120 }}>
					{#if division.services.length > 0}
						<div class="grid gap-x-8 gap-y-1 sm:grid-cols-2">
							{#each division.services as service (service.slug)}
								<a
									href={`/fr/services/${division.slug}/${service.slug}`}
									class="group flex items-start gap-2 rounded-input px-2 py-2.5 text-sm text-ink-800 hover:bg-ink-900/5 hover:text-ink-950"
								>
									<span
										class="mt-2 h-1 w-1 shrink-0 rounded-full bg-green-500 transition-transform group-hover:scale-150"
									></span>
									<span>{service.title}</span>
								</a>
							{/each}
						</div>
					{:else}
						<p class="text-sm text-ink-800/60">
							Les services de ce pôle seront publiés à son ouverture.
						</p>
					{/if}
				</div>
			</div>
		</div>
	</section>
{/each}
