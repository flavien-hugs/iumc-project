<script lang="ts">
	import { FacebookLogo, LinkedinLogo, WhatsappLogo, XLogo } from 'phosphor-svelte';
	import { page } from '$app/state';
	import Seo from '$lib/components/Seo.svelte';
	import { articleIcon, formatPublishedDate, stripHtml } from '$lib/content';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const article = $derived(data.article);
	const Icon = $derived(articleIcon(article.category));

	const articleJsonLd = $derived({
		'@context': 'https://schema.org',
		'@type': 'Article',
		headline: article.title,
		description: stripHtml(article.summary) || article.title,
		datePublished: article.published_at ?? undefined,
		author: article.author_name
			? { '@type': 'Person', name: article.author_name }
			: undefined,
		publisher: {
			'@type': 'Organization',
			name: 'Ivoire Univers Multiservices et Commerces (IUMC)'
		}
	});

	const shareUrl = $derived(page.url.href);
	const shareText = $derived(encodeURIComponent(article.title));

	const shareLinks = $derived([
		{
			label: 'WhatsApp',
			icon: WhatsappLogo,
			href: `https://wa.me/?text=${shareText}%20${encodeURIComponent(shareUrl)}`
		},
		{
			label: 'Facebook',
			icon: FacebookLogo,
			href: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`
		},
		{
			label: 'LinkedIn',
			icon: LinkedinLogo,
			href: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`
		},
		{
			label: 'X',
			icon: XLogo,
			href: `https://twitter.com/intent/tweet?text=${shareText}&url=${encodeURIComponent(shareUrl)}`
		}
	]);
</script>

<Seo
	title={`${article.title}, IUMC`}
	description={stripHtml(article.summary) || article.title}
	type="article"
	jsonLd={articleJsonLd}
/>

<article class="relative mx-auto max-w-2xl overflow-hidden px-6 pt-16 pb-20 lg:px-10">
	<Icon class="pointer-events-none absolute top-10 -right-10 hidden h-52 w-52 text-ink-900/5 sm:block" />
	<a href="/fr/actualites" class="text-sm font-medium text-ink-800/70 hover:text-ink-950">
		Actualités et conseils
	</a>

	{#if article.category}
		<span class="mt-4 block text-xs font-medium text-green-600">{article.category}</span>
	{/if}
	<h1 class="mt-2 text-3xl font-semibold text-ink-950 md:text-4xl">{article.title}</h1>
	<p class="mt-3 text-sm text-ink-800/50">
		{article.author_name ?? 'IUMC'} · {formatPublishedDate(article.published_at)}
	</p>

	{#if article.body}
		<div class="iumc-rich-text mt-8 text-base leading-relaxed text-ink-800/90">
			{@html article.body}
		</div>
	{/if}

	<div class="mt-10 flex items-center gap-3 border-t border-ink-900/10 pt-6">
		<span class="text-sm text-ink-800/60">Partager :</span>
		{#each shareLinks as share (share.label)}
			<a
				href={share.href}
				target="_blank"
				rel="noopener noreferrer"
				aria-label={`Partager sur ${share.label}`}
				class="flex h-9 w-9 items-center justify-center rounded-full border border-ink-900/15 text-ink-800 hover:border-green-500 hover:text-green-600"
			>
				<share.icon size={16} />
			</a>
		{/each}
	</div>
</article>
