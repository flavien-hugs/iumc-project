<script lang="ts">
	import { CaretDown, List, X } from 'phosphor-svelte';
	import { fly } from 'svelte/transition';
	import { page } from '$app/state';
	import { divisionIcon, type PublicDivision } from '$lib/content';

	function prefersReducedMotion(): boolean {
		return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
	}

	const CTA_LABEL = 'Demander un accompagnement';

	const divisions = $derived((page.data.divisions ?? []) as PublicDivision[]);

	const links = [
		{ href: '/fr/implantations', label: 'Implantations' },
		{ href: '/fr/actualites', label: 'Actualités' },
		{ href: '/fr/contact', label: 'Contact' }
	];

	function isActive(href: string): boolean {
		return page.url.pathname === href || page.url.pathname.startsWith(`${href}/`);
	}

	const divisionsActive = $derived(isActive('/fr/services'));

	let mobileOpen = $state(false);
	let desktopDivisionsOpen = $state(false);
	let divisionsMenuEl: HTMLDivElement | undefined = $state();

	function onDocumentClick(event: MouseEvent) {
		if (divisionsMenuEl && !divisionsMenuEl.contains(event.target as Node)) {
			desktopDivisionsOpen = false;
		}
	}

	function onDocumentKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape') desktopDivisionsOpen = false;
	}

	$effect(() => {
		if (!desktopDivisionsOpen) return;
		// Attache l'écouteur au tick suivant : sinon, sur le même clic qui
		// ouvre le menu, l'évènement continue de remonter jusqu'à document
		// et se fait intercepter par ce nouvel écouteur, refermant le menu
		// aussitôt ouvert.
		const timeoutId = setTimeout(() => {
			document.addEventListener('click', onDocumentClick);
			document.addEventListener('keydown', onDocumentKeydown);
		}, 0);
		return () => {
			clearTimeout(timeoutId);
			document.removeEventListener('click', onDocumentClick);
			document.removeEventListener('keydown', onDocumentKeydown);
		};
	});

	function closeAll() {
		mobileOpen = false;
		desktopDivisionsOpen = false;
	}

	// En haut de page, le header se fond dans le hero ; passé ce seuil de
	// scroll il retrouve un fond, un flou et une hauteur réduite.
	let scrolled = $state(false);

	$effect(() => {
		function onScroll() {
			scrolled = window.scrollY > 60;
		}
		onScroll();
		window.addEventListener('scroll', onScroll, { passive: true });
		return () => window.removeEventListener('scroll', onScroll);
	});

	let mobilePanelEl: HTMLDivElement | undefined = $state();

	// Piège de focus léger : focus initial dans le panneau + fermeture par
	// Échap (même principe que ConfirmDialog/Drawer, cf. packages/ui).
	$effect(() => {
		if (!mobileOpen) return;
		const previousOverflow = document.body.style.overflow;
		document.body.style.overflow = 'hidden';
		const frameId = requestAnimationFrame(() => {
			mobilePanelEl?.querySelector<HTMLElement>('a, button')?.focus();
		});
		function onKeydown(event: KeyboardEvent) {
			if (event.key === 'Escape') closeAll();
		}
		document.addEventListener('keydown', onKeydown);
		return () => {
			document.body.style.overflow = previousOverflow;
			cancelAnimationFrame(frameId);
			document.removeEventListener('keydown', onKeydown);
		};
	});
</script>

<header
	class={`sticky top-0 z-40 border-b transition-colors duration-300 ${
		scrolled
			? 'border-ink-900/10 bg-paper-50/95 shadow-sm shadow-ink-950/5 backdrop-blur-sm'
			: 'border-transparent bg-transparent'
	}`}
>
	<div
		class={`mx-auto flex max-w-7xl items-center justify-between px-6 transition-[height] duration-300 lg:px-10 ${scrolled ? 'h-14' : 'h-18'}`}
	>
		<a href="/fr" class="flex items-center gap-2.5" aria-label="IUMC, accueil">
			<img src="/logo-iumc-embleme.png" alt="" class="h-9 w-auto" />
			<img src="/logo-iumc-wordmark.png" alt="IUMC" class="h-4.5 w-auto" />
		</a>

		<nav class="hidden items-center gap-8 md:flex" aria-label="Navigation principale">
			{#snippet navUnderline(active: boolean)}
				<span
					class={`absolute -bottom-1.5 left-0 h-[1.5px] w-full origin-left bg-green-500 transition-transform duration-300 ${active ? 'scale-x-100' : 'scale-x-0 group-hover:scale-x-100'}`}
				></span>
			{/snippet}

			<a
				href="/fr/qui-sommes-nous"
				class={`group relative text-sm font-bold transition-colors ${isActive('/fr/qui-sommes-nous') ? 'text-green-600' : 'text-ink-800 hover:text-green-600'}`}
			>
				Qui sommes-nous
				{@render navUnderline(isActive('/fr/qui-sommes-nous'))}
			</a>

			<div
				class="relative"
				bind:this={divisionsMenuEl}
			>
				<button
					type="button"
					class={`group relative flex items-center gap-1 text-sm font-bold transition-colors ${desktopDivisionsOpen || divisionsActive ? 'text-green-600' : 'text-ink-800 hover:text-green-600'}`}
					aria-expanded={desktopDivisionsOpen}
					aria-haspopup="true"
					onclick={() => (desktopDivisionsOpen = !desktopDivisionsOpen)}
				>
					Nos pôles
					<CaretDown size={14} class={`transition-transform ${desktopDivisionsOpen ? 'rotate-180' : ''}`} />
					{@render navUnderline(desktopDivisionsOpen || divisionsActive)}
				</button>

				{#if desktopDivisionsOpen}
					<div
						class="absolute top-full left-1/2 mt-3 w-84 -translate-x-1/2 rounded-card border border-ink-900/10 bg-paper-50 p-2 shadow-lg shadow-ink-950/10"
						role="menu"
					>
						<a
							href="/fr/services"
							class="block rounded-input px-3 py-2 text-sm font-bold text-ink-950 hover:bg-ink-900/5"
							onclick={() => (desktopDivisionsOpen = false)}
						>
							Tous nos pôles
						</a>
						<div class="my-1 border-t border-ink-900/10"></div>
						{#each divisions as division (division.slug)}
							{@const Icon = divisionIcon(division.slug)}
							<a
								href={`/fr/services/${division.slug}`}
								class="flex items-start gap-3 rounded-input px-3 py-2.5 hover:bg-ink-900/5"
								onclick={() => (desktopDivisionsOpen = false)}
							>
								<Icon class="mt-0.5 h-5 w-5 shrink-0 text-ink-800/60" />
								<span class="flex-1">
									<span class="block text-sm font-semibold text-ink-900">{division.name}</span>
									{#if division.short_description}
										<span class="mt-0.5 line-clamp-2 block text-xs text-ink-800/60">
											{division.short_description}
										</span>
									{/if}
								</span>
								{#if division.status === 'coming_soon'}
									<span
										class="mt-0.5 rounded-pill bg-cyan-600/10 px-2 py-0.5 text-[11px] font-medium text-cyan-600"
									>
										Bientôt
									</span>
								{/if}
							</a>
						{/each}
					</div>
				{/if}
			</div>

			{#each links as link (link.href)}
				<a
					href={link.href}
					class={`group relative text-sm font-bold transition-colors ${isActive(link.href) ? 'text-green-600' : 'text-ink-800 hover:text-green-600'}`}
				>
					{link.label}
					{@render navUnderline(isActive(link.href))}
				</a>
			{/each}
		</nav>

		<a
			href="/fr/demande"
			class="hidden rounded-pill bg-green-500 px-5 py-2.5 text-sm font-medium text-ink-950 transition-transform hover:bg-green-600 active:scale-[0.98] sm:inline-flex"
		>
			{CTA_LABEL}
		</a>

		<button
			type="button"
			class="inline-flex items-center justify-center rounded-input p-2 text-ink-950 md:hidden"
			aria-label={mobileOpen ? 'Fermer le menu' : 'Ouvrir le menu'}
			aria-expanded={mobileOpen}
			onclick={() => (mobileOpen = !mobileOpen)}
		>
			{#if mobileOpen}
				<X size={24} />
			{:else}
				<List size={24} />
			{/if}
		</button>
	</div>

	{#if mobileOpen}
		<!-- Menu mobile plein écran : grande typographie éditoriale, apparition
		     séquentielle des liens, scroll du body bloqué (voir l'$effect). -->
		<div
			bind:this={mobilePanelEl}
			class="fixed inset-0 z-50 flex flex-col overflow-y-auto bg-ink-950 md:hidden"
			transition:fly={{ y: -12, duration: prefersReducedMotion() ? 0 : 220 }}
		>
			<div class="flex h-18 shrink-0 items-center justify-between px-6">
				<a href="/fr" class="flex items-center gap-2.5" aria-label="IUMC, accueil" onclick={closeAll}>
					<img src="/logo-iumc-embleme.png" alt="" class="h-9 w-auto" />
					<img src="/logo-iumc-wordmark.png" alt="IUMC" class="h-4.5 w-auto" />
				</a>
				<button
					type="button"
					class="inline-flex items-center justify-center rounded-input p-2 text-paper-50"
					aria-label="Fermer le menu"
					onclick={closeAll}
				>
					<X size={26} />
				</button>
			</div>

			<nav
				class="flex flex-1 flex-col justify-center gap-3 px-8 py-10"
				aria-label="Navigation principale mobile"
			>
				{#each [{ href: '/fr/qui-sommes-nous', label: 'Qui sommes-nous' }, ...links] as link, i (link.href)}
					<a
						href={link.href}
						onclick={closeAll}
						in:fly={{
							y: 24,
							duration: prefersReducedMotion() ? 0 : 400,
							delay: prefersReducedMotion() ? 0 : 60 + i * 70
						}}
						class={`font-display text-4xl leading-tight font-bold ${isActive(link.href) ? 'text-green-500' : 'text-paper-50 hover:text-green-200'}`}
					>
						{link.label}
					</a>
				{/each}

				<div
					in:fly={{
						y: 24,
						duration: prefersReducedMotion() ? 0 : 400,
						delay: prefersReducedMotion() ? 0 : 60 + (links.length + 1) * 70
					}}
					class="mt-8 border-t border-paper-100/10 pt-6"
				>
					<a
						href="/fr/services"
						class={`text-xs font-bold tracking-wide uppercase ${divisionsActive ? 'text-green-500' : 'text-paper-100/50 hover:text-paper-100'}`}
						onclick={closeAll}
					>
						Nos pôles
					</a>
					<div class="mt-3 flex flex-col gap-2.5">
						{#each divisions as division (division.slug)}
							{@const Icon = divisionIcon(division.slug)}
							<a
								href={`/fr/services/${division.slug}`}
								class="flex items-center gap-3 text-base font-semibold text-paper-100/85 hover:text-green-200"
								onclick={closeAll}
							>
								<Icon class="h-5 w-5 shrink-0 text-green-500/70" />
								{division.name}
								{#if division.status === 'coming_soon'}
									<span
										class="rounded-pill bg-paper-100/10 px-2 py-0.5 text-[11px] font-medium text-paper-100/70"
									>
										Bientôt
									</span>
								{/if}
							</a>
						{/each}
					</div>
				</div>

				<a
					href="/fr/demande"
					onclick={closeAll}
					in:fly={{
						y: 24,
						duration: prefersReducedMotion() ? 0 : 400,
						delay: prefersReducedMotion() ? 0 : 60 + (links.length + 2) * 70
					}}
					class="mt-8 rounded-pill bg-green-500 px-6 py-3.5 text-center text-sm font-medium text-ink-950"
				>
					{CTA_LABEL}
				</a>
			</nav>
		</div>
	{/if}
</header>
