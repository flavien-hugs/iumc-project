<script lang="ts">
	import { ArrowRight, WhatsappLogo } from 'phosphor-svelte';
	import { divisionIcon } from '$lib/content';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const division = $derived(data.division);
	const service = $derived(data.service);
	const relatedFaq = $derived(data.faqs);
	const Icon = $derived(divisionIcon(division.slug));

	const steps = [
		{
			title: 'Premier échange',
			description: 'Vous décrivez votre besoin via le formulaire, par téléphone ou WhatsApp.'
		},
		{
			title: 'Analyse du dossier',
			description: 'Un conseiller examine votre situation et les pièces déjà disponibles.'
		},
		{
			title: "Proposition d'accompagnement",
			description: 'IUMC vous présente les étapes et le mode de collaboration adaptés.'
		},
		{
			title: "Suivi jusqu'à la clôture",
			description: 'Le dossier est suivi jusqu’à son aboutissement, avec des points réguliers.'
		}
	];


</script>

<svelte:head>
	<title>{service.title}, IUMC</title>
	<meta name="description" content={service.summary ?? service.title} />
</svelte:head>

<section class="relative mx-auto max-w-4xl overflow-hidden px-6 pt-16 pb-8 lg:px-10">
	<Icon class="pointer-events-none absolute top-8 -right-8 hidden h-56 w-56 text-ink-900/5 sm:block" />
	<a
		href={`/fr/services/${division.slug}`}
		class="text-sm font-medium text-ink-800/70 hover:text-ink-950"
	>
		{division.name}
	</a>
	<h1 class="mt-3 text-4xl font-semibold text-ink-950">{service.title}</h1>
	{#if service.summary}
		<p class="mt-4 max-w-[60ch] text-ink-800/80">{service.summary}</p>
	{/if}
	{#if service.description}
		<p class="mt-3 max-w-[60ch] text-sm text-ink-800/70">{service.description}</p>
	{/if}

	<div class="mt-8 flex flex-wrap items-center gap-4">
		<a
			href={`/fr/demande?division=${division.slug}&service=${service.slug}`}
			class="inline-flex items-center gap-2 rounded-pill bg-gold-500 px-6 py-3 text-sm font-medium text-ink-950 transition-transform hover:bg-gold-600 active:scale-[0.98]"
		>
			Demander un accompagnement
			<ArrowRight size={16} />
		</a>
		<a
			href="https://wa.me/225XXXXXXXXXX"
			target="_blank"
			rel="noopener noreferrer"
			class="inline-flex items-center gap-2 rounded-pill border border-ink-900/20 px-6 py-3 text-sm font-medium text-ink-900 hover:border-ink-900/40"
		>
			<WhatsappLogo size={18} weight="fill" />
			Échanger sur WhatsApp
		</a>
	</div>
</section>

<section class="mx-auto max-w-4xl px-6 pb-16 lg:px-10">
	<h2 class="text-xl font-semibold text-ink-950">Comment se déroule l'accompagnement</h2>
	<ol class="mt-6 grid gap-x-8 gap-y-6 sm:grid-cols-2">
		{#each steps as step, i (step.title)}
			<li class="flex gap-4">
				<span
					class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-ink-900/5 text-sm font-medium text-ink-900"
				>
					{i + 1}
				</span>
				<div>
					<p class="font-medium text-ink-950">{step.title}</p>
					<p class="mt-1 text-sm text-ink-800/70">{step.description}</p>
				</div>
			</li>
		{/each}
	</ol>

	<p class="mt-8 rounded-input bg-paper-100 px-4 py-3 text-sm text-ink-800/70">
		Les documents précisément demandés dépendent de votre situation. Ils vous seront
		communiqués par un conseiller lors du premier échange, avant tout engagement.
	</p>
</section>

{#if relatedFaq.length > 0}
	<section class="bg-paper-100">
		<div class="mx-auto max-w-4xl px-6 py-14 lg:px-10">
			<h2 class="text-xl font-semibold text-ink-950">Questions fréquentes</h2>
			<dl class="mt-6 divide-y divide-ink-900/10">
				{#each relatedFaq as item (item.question)}
					<div class="py-4">
						<dt class="font-medium text-ink-950">{item.question}</dt>
						<dd class="iumc-rich-text mt-1.5 text-sm text-ink-800/70">{@html item.answer}</dd>
					</div>
				{/each}
			</dl>
		</div>
	</section>
{/if}
