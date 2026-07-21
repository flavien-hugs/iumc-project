<script lang="ts">
	import { page } from '$app/state';

	let {
		title,
		description,
		type = 'website',
		jsonLd
	}: {
		title: string;
		description: string;
		type?: 'website' | 'article';
		jsonLd?: Record<string, unknown>;
	} = $props();

	// Canonique sans query string : les variantes filtrées (recherche,
	// pagination) pointent vers la ressource de base.
	const canonical = $derived(`${page.url.origin}${page.url.pathname}`);

	// Le remplacement de « < » neutralise toute fermeture de balise script
	// qui viendrait d'une valeur de contenu.
	const jsonLdTag = $derived(
		jsonLd
			? `<script type="application/ld+json">${JSON.stringify(jsonLd).replace(/</g, '\\u003c')}<\/script>`
			: null
	);
</script>

<svelte:head>
	<title>{title}</title>
	<meta name="description" content={description} />
	<link rel="canonical" href={canonical} />
	<meta property="og:title" content={title} />
	<meta property="og:description" content={description} />
	<meta property="og:type" content={type} />
	<meta property="og:url" content={canonical} />
	<meta property="og:site_name" content="IUMC" />
	<meta property="og:locale" content="fr_FR" />
	<meta property="og:image" content={`${page.url.origin}/logo-iumc.jpeg`} />
	{#if jsonLdTag}
		{@html jsonLdTag}
	{/if}
</svelte:head>
