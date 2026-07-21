<script lang="ts">
  import { ArrowRight, WhatsappLogo } from "phosphor-svelte";
  import { page } from "$app/state";
  import Seo from "$lib/components/Seo.svelte";
  import CoteDIvoireMap from "$lib/illustrations/CoteDIvoireMap.svelte";
  import SenufoFrieze from "$lib/illustrations/SenufoFrieze.svelte";
  import GoldWeightMotif from "$lib/illustrations/GoldWeightMotif.svelte";
  import KenteMotif from "$lib/illustrations/KenteMotif.svelte";
  import ArticleCard from "$lib/components/ArticleCard.svelte";
  import { reveal } from "$lib/actions/reveal";
  import { divisionIcon, type PublicDivision } from "$lib/content";
  import type { PageProps } from "./$types";

  let { data }: PageProps = $props();

  const divisions = $derived(data.divisions as PublicDivision[]);
  const legalDivision = $derived(
    divisions.find((item) => item.slug === "juridique"),
  );
  const realEstateDivision = $derived(
    divisions.find((item) => item.slug === "foncier-immobilier"),
  );
  const agroDivision = $derived(
    divisions.find((item) => item.slug === "agropastoral"),
  );
  const LegalIcon = divisionIcon("juridique");
  const RealEstateIcon = divisionIcon("foncier-immobilier");
  const AgroIcon = divisionIcon("agropastoral");

  const latestArticles = $derived(data.articles);

  const values = $derived(data.company.about.values);
  const advantages = $derived(data.company.about.differentiators);

  const clientGroups = [
    "Particuliers",
    "Entreprises",
    "Industriels",
    "Promoteurs immobiliers",
    "Communautés villageoises",
    "Investisseurs",
  ];

  // Bandeau défilant : segments réels des pôles (CDC), en rappel de l'offre.
  const segments = [
    "Bail commercial",
    "Bail emphytéotique industriel",
    "Partenariats & protocoles d'accord",
    "Prévention des litiges fonciers",
    "Foncier urbain & industriel",
    "Accompagnement immobilier",
    "Audit documentaire",
    "Dossiers ACD & CMPF",
    "Accompagnement des promoteurs",
    "Business plans",
    "Agropastoral — bientôt",
  ];

  // Rythme typographique de la section valeurs : tailles et teintes alternées.
  const VALUE_SIZES = [
    "text-4xl md:text-6xl",
    "text-2xl md:text-4xl",
    "text-3xl md:text-5xl",
  ];
  const VALUE_COLORS = ["text-paper-50", "text-green-500", "text-paper-100/70"];

  const orgJsonLd = $derived({
    "@context": "https://schema.org",
    "@type": "Organization",
    name: "Ivoire Univers Multiservices et Commerces (IUMC)",
    url: `${page.url.origin}/fr`,
    email: "contact@iumc.ci",
    address: {
      "@type": "PostalAddress",
      addressLocality: "Bouaké",
      addressCountry: "CI",
    },
  });
</script>

<Seo
  title="IUMC, accompagnement juridique, foncier, immobilier et industriel"
  description="IUMC accompagne particuliers, entreprises et investisseurs pour leurs démarches juridiques, foncières, immobilières et industrielles en Côte d'Ivoire, depuis Bouaké."
  jsonLd={orgJsonLd}
/>

<!-- Hero : split asymétrique, texte + carte des implantations (parallaxe),
     bordé d'un lé kente vertical comme une lisière de pagne tissé -->
<section
  class="relative mx-auto grid max-w-7xl items-center gap-12 overflow-hidden px-6 pt-16 pb-20 md:grid-cols-[1.2fr_1fr] lg:min-h-[72vh] lg:px-10 lg:pt-20"
>
  <KenteMotif
    patternId="kente-hero"
    class="pointer-events-none absolute inset-y-0 right-0 hidden w-10 text-ink-700 opacity-20 lg:block"
  />
  <!-- Filigrane : l'emblème du logo en profondeur derrière la carte -->
  <img
    src="/logo-iumc-embleme.png"
    alt=""
    aria-hidden="true"
    class="parallax-lent pointer-events-none absolute top-1/2 -right-20 hidden w-130 -translate-y-1/2 opacity-4 select-none lg:block"
  />
  <div use:reveal>
    <p class="text-xs font-medium tracking-[0.25em] text-green-600 uppercase">
      Juridique · Foncier & immobilier · Agropastoral
    </p>
    <h1
      class="mt-5 max-w-[16ch] text-5xl leading-[1.02] font-semibold text-ink-950 md:text-6xl lg:text-7xl xl:text-8xl"
    >
      La <span class="font-bold text-green-600">sécurité</span> juridique de vos
      projets.
    </h1>
    <p
      class="mt-6 max-w-[46ch] text-base leading-relaxed text-ink-800/80 lg:text-lg"
    >
      IUMC accompagne particuliers, entreprises et investisseurs dans leurs
      démarches juridiques, foncières, immobilières et industrielles à Bouaké.
    </p>
    <div class="mt-8 flex flex-wrap items-center gap-4">
      <a
        href="/fr/demande"
        class="inline-flex items-center gap-2 rounded-pill bg-green-500 px-6 py-3 text-sm font-medium text-ink-950 transition-transform hover:bg-green-600 active:scale-[0.98]"
      >
        Demander un accompagnement
        <ArrowRight size={16} />
      </a>
      <a
        href="/fr/services"
        class="text-sm font-medium text-ink-900 underline decoration-ink-900/30 underline-offset-4 hover:decoration-ink-900"
      >
        Découvrir nos pôles
      </a>
    </div>
  </div>

  <div
    class="parallax-lent mx-auto w-full max-w-sm md:max-w-none"
    use:reveal={{ delay: 120 }}
  >
    <CoteDIvoireMap labels class="h-auto w-full" />
  </div>
</section>

<!-- Bandeau défilant des segments d'intervention (pause au survol) -->
<div class="marquee-band overflow-hidden border-y border-ink-900/10">
  <div class="marquee-track flex w-max">
    {#each [0, 1] as copy (copy)}
      <ul
        class="flex items-center gap-10 py-3.5 pr-10 pl-6 text-sm whitespace-nowrap text-ink-800/70"
        aria-hidden={copy === 1}
      >
        {#each segments as segment (segment)}
          <li class="flex items-center gap-10">
            {segment}
            <span aria-hidden="true" class="text-green-500">·</span>
          </li>
        {/each}
      </ul>
    {/each}
  </div>
</div>

<div class="mx-auto max-w-7xl px-6 pt-8 lg:px-10">
  <SenufoFrieze class="h-6 w-full text-gold-500/40" />
</div>

<!-- Nos pôles d'activité : bento 1 tuile en avant + 2 secondaires (3 items, 3 cellules) -->
<section class="mx-auto max-w-7xl px-6 pb-20 lg:px-10">
  <h2 class="text-3xl font-semibold text-ink-950 md:text-4xl">
    Nos pôles d'activité
  </h2>
  <p class="mt-3 max-w-[60ch] text-ink-800/80">
    Trois domaines d'intervention, pensés pour se compléter selon la nature de
    votre projet.
  </p>

  <div class="mt-10 grid gap-4 md:grid-cols-2">
    {#if legalDivision}
      <a
        href={`/fr/services/${legalDivision.slug}`}
        use:reveal
        class="group relative flex flex-col justify-between gap-8 overflow-hidden rounded-card bg-ink-950 p-8 text-paper-50 transition duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-ink-950/15 motion-reduce:transition-none motion-reduce:hover:translate-y-0 md:col-span-2 md:flex-row md:items-end"
      >
        <KenteMotif
          patternId="kente-pole-juridique"
          class="pointer-events-none absolute inset-y-0 right-0 w-8 text-paper-50 opacity-10"
        />
        <LegalIcon
          class="pointer-events-none absolute -top-8 right-8 h-48 w-48 text-paper-50/6"
        />
        <div>
          <span class="font-display text-sm tracking-[0.35em] text-green-500/70"
            >01</span
          >
          <LegalIcon class="mt-3 h-10 w-10 text-green-500" />
          <h3 class="mt-4 text-2xl font-semibold">{legalDivision.name}</h3>
          <p class="mt-2 max-w-[48ch] text-sm text-paper-100/70">
            {legalDivision.short_description}
          </p>
        </div>
        <span
          class="inline-flex items-center gap-4 text-sm font-medium text-green-500 group-hover:text-green-200"
        >
          <span class="text-xs text-paper-100/50"
            >{legalDivision.services.length} services</span
          >
          Voir le pôle
          <ArrowRight
            size={16}
            class="transition-transform group-hover:translate-x-1"
          />
        </span>
      </a>
    {/if}

    {#if realEstateDivision}
      <a
        href={`/fr/services/${realEstateDivision.slug}`}
        use:reveal={{ delay: 100 }}
        class="group relative flex flex-col justify-between gap-6 overflow-hidden rounded-card bg-paper-100 p-8 transition duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-ink-950/8 motion-reduce:transition-none motion-reduce:hover:translate-y-0"
      >
        <RealEstateIcon
          class="pointer-events-none absolute -right-6 -bottom-8 h-44 w-44 text-ink-900/6"
        />
        <div>
          <span class="font-display text-sm tracking-[0.35em] text-ink-800/40"
            >02</span
          >
          <RealEstateIcon class="mt-3 h-10 w-10 text-ink-900" />
          <h3 class="mt-4 text-xl font-semibold text-ink-950">
            {realEstateDivision.name}
          </h3>
          <p class="mt-2 text-sm text-ink-800/80">
            {realEstateDivision.short_description}
          </p>
        </div>
        <span
          class="inline-flex items-center gap-4 text-sm font-medium text-green-600"
        >
          <span class="text-xs text-ink-800/50"
            >{realEstateDivision.services.length} services</span
          >
          Voir le pôle
          <ArrowRight
            size={16}
            class="transition-transform group-hover:translate-x-1"
          />
        </span>
      </a>
    {/if}

    {#if agroDivision}
      <div
        use:reveal={{ delay: 180 }}
        class="relative flex flex-col justify-between gap-6 overflow-hidden rounded-card bg-cyan-100 p-8"
      >
        <AgroIcon
          class="pointer-events-none absolute -right-8 -bottom-8 h-44 w-44 text-cyan-600/8"
        />
        <div>
          <div class="flex items-center justify-between">
            <span
              class="font-display text-sm tracking-[0.35em] text-cyan-600/60"
              >03</span
            >
            <span
              class="rounded-pill bg-cyan-600/10 px-3 py-1 text-xs font-medium text-cyan-600"
            >
              Bientôt disponible
            </span>
          </div>
          <AgroIcon class="mt-3 h-10 w-10 text-cyan-600" />
          <h3 class="mt-4 text-xl font-semibold text-ink-950">
            {agroDivision.name}
          </h3>
          <p class="mt-2 text-sm text-ink-800/80">
            {agroDivision.short_description}
          </p>
        </div>
      </div>
    {/if}
  </div>
</section>

<!-- Ce qui nous distingue : liste 2 colonnes + clientèles en filet -->
<section class="mx-auto max-w-7xl px-6 pb-20 lg:px-10">
  <h2 class="text-3xl font-semibold text-ink-950 md:text-4xl">
    Ce qui distingue IUMC
  </h2>
  <p class="mt-3 max-w-[60ch] text-ink-800/80">
    Un modèle pensé pour <span class="font-bold text-green-600"
      >simplifier des démarches</span
    >
    habituellement fragmentées entre plusieurs interlocuteurs.
  </p>

  <dl class="mt-12 grid gap-x-16 gap-y-10 md:grid-cols-2">
    {#each advantages as advantage, i (advantage.title)}
      <div
        use:reveal={{ delay: i * 90 }}
        class={`relative border-t border-ink-900/10 pt-6 pl-16 ${i % 2 === 1 ? "md:translate-y-8" : ""}`}
      >
        <span
          aria-hidden="true"
          class="font-display absolute top-5 left-0 text-4xl font-bold text-green-500/35"
        >
          {String(i + 1).padStart(2, "0")}
        </span>
        <dt class="text-lg font-semibold text-ink-950">{advantage.title}</dt>
        <dd class="iumc-rich-text mt-2 text-sm text-ink-800/80">
          {@html advantage.description}
        </dd>
      </div>
    {/each}
  </dl>

  <div
    class="mt-10 flex flex-wrap items-center gap-x-3 gap-y-2 border-t border-ink-900/10 pt-6"
  >
    <span class="text-sm font-medium text-ink-950">Nous accompagnons :</span>
    {#each clientGroups as group (group)}
      <span class="rounded-pill bg-ink-900/5 px-3 py-1 text-xs text-ink-800">
        {group}
      </span>
    {/each}
  </div>
</section>

<!-- Nos implantations : carte étiquetée dominante + texte + jauge flottante,
     colonnes asymétriques (inverse du hero pour rompre la répétition) -->
<section
  class="mx-auto grid max-w-7xl items-center gap-12 overflow-hidden px-6 pb-24 md:grid-cols-[1fr_1.3fr] lg:px-10"
>
  <div use:reveal>
    <p class="text-xs font-medium tracking-[0.25em] text-green-600 uppercase">
      Implantations
    </p>
    <h2 class="mt-4 text-3xl font-semibold text-ink-950 md:text-4xl">
      Une présence qui s'étend
    </h2>
    <p class="mt-4 max-w-[52ch] text-ink-800/80">
      Le siège d'IUMC est situé à Bouaké, quartier Koko. L'entreprise prévoit
      d'ouvrir
      <span class="font-bold text-green-600">progressivement</span> des agences dans
      plusieurs villes de Côte d'Ivoire, dont Yamoussoukro, Abidjan, San Pedro et
      Korhogo.
    </p>
    <a
      href="/fr/implantations"
      class="mt-6 inline-flex items-center gap-2 text-sm font-medium text-ink-900 underline decoration-ink-900/30 underline-offset-4 hover:decoration-ink-900"
    >
      Voir toutes nos implantations
      <ArrowRight size={16} />
    </a>
  </div>
  <div
    class="relative mx-auto w-full max-w-md md:max-w-none"
    use:reveal={{ delay: 120 }}
  >
    <div class="parallax-inverse">
      <CoteDIvoireMap labels class="h-auto w-full" />
    </div>
    <!-- Jauge flottante : superposition qui casse le cadre de la carte -->
    <div
      class="absolute -bottom-4 left-4 rounded-card border border-ink-900/10 bg-paper-50 px-5 py-3 shadow-lg shadow-ink-950/8 md:left-8"
    >
      <p class="font-display text-2xl font-bold text-green-600">
        {Math.max(0, data.locationsCount - 1)}
      </p>
      <p class="text-xs text-ink-800/60">villes en expansion</p>
    </div>
  </div>
</section>

<!-- Nos valeurs : manifeste typographique sur fond sombre — rupture de rythme
     volontaire (seule autre section sombre : le CTA final) avant la grille
     d'actualités qui suit -->
<section class="relative overflow-hidden bg-ink-950 py-20">
  <GoldWeightMotif
    class="parallax-lent pointer-events-none absolute top-1/2 left-1/2 h-105 w-105 -translate-x-1/2 -translate-y-1/2 text-paper-50/5"
  />
  <div class="relative mx-auto max-w-5xl px-6 text-center lg:px-10" use:reveal>
    <p
      class="text-xs font-medium tracking-[0.25em] text-green-500/70 uppercase"
    >
      Nos valeurs
    </p>
    <div
      class="mt-8 flex flex-wrap items-baseline justify-center gap-x-5 gap-y-3"
    >
      {#each values as value, i (value)}
        <span
          class={`font-display font-semibold ${VALUE_SIZES[i % VALUE_SIZES.length]} ${VALUE_COLORS[i % VALUE_COLORS.length]}`}
        >
          {value}
        </span>
      {/each}
    </div>
  </div>
</section>

<!-- Actualités et conseils : grille de cartes -->
<section class="mx-auto max-w-7xl px-6 py-20 lg:px-10">
  <div class="flex flex-wrap items-end justify-between gap-4">
    <div>
      <h2 class="text-3xl font-semibold text-ink-950 md:text-4xl">
        Actualités et conseils
      </h2>
      <p class="mt-3 max-w-[60ch] text-ink-800/80">
        Des repères pratiques sur les démarches foncières, immobilières et
        juridiques.
      </p>
    </div>
    <a
      href="/fr/actualites"
      class="inline-flex items-center gap-2 text-sm font-medium text-ink-900 underline decoration-ink-900/30 underline-offset-4 hover:decoration-ink-900"
    >
      Toutes les actualités
      <ArrowRight size={16} />
    </a>
  </div>

  {#if latestArticles.length > 0}
    <div class="mt-10 grid gap-6 md:grid-cols-2">
      <ArticleCard article={latestArticles[0]} featured />
      <div class="grid gap-6">
        {#each latestArticles.slice(1, 3) as article, i (article.slug)}
          <ArticleCard {article} revealDelay={i * 90 + 90} />
        {/each}
      </div>
    </div>
  {/if}
</section>

<!-- Appel à l'action final, sur fond tissé kente + filigrane emblème (écho au hero) -->
<section class="relative overflow-hidden bg-ink-950">
  <KenteMotif
    patternId="kente-cta"
    class="pointer-events-none absolute inset-0 h-full w-full text-paper-50 opacity-5"
  />
  <img
    src="/logo-iumc-embleme.png"
    alt=""
    aria-hidden="true"
    class="pointer-events-none absolute -top-16 -left-16 hidden w-110 opacity-6 select-none lg:block"
  />
  <div class="relative mx-auto max-w-7xl px-6 pt-10 lg:px-10">
    <SenufoFrieze class="h-6 w-full text-gold-500/30" />
  </div>
  <div
    class="relative mx-auto flex max-w-7xl flex-col items-start gap-6 px-6 pt-6 pb-16 lg:flex-row lg:items-center lg:justify-between lg:px-10"
    use:reveal
  >
    <div>
      <h2 class="max-w-[24ch] text-4xl font-semibold text-paper-50 md:text-5xl">
        Prêt à <span class="font-bold text-green-500">sécuriser</span> votre projet
        ?
      </h2>
      <p class="mt-3 max-w-[48ch] text-paper-100/70">
        Décrivez votre besoin, un membre de l'équipe IUMC vous recontacte.
      </p>
    </div>
    <div
      class="flex flex-nowrap items-center gap-3 overflow-x-auto pb-1 sm:gap-4"
    >
      <a
        href="/fr/demande"
        class="inline-flex shrink-0 items-center gap-2 rounded-pill bg-green-500 px-5 py-2.5 text-sm font-medium whitespace-nowrap text-ink-950 transition-transform hover:bg-green-600 active:scale-[0.98] sm:px-6 sm:py-3"
      >
        Demander un accompagnement
        <ArrowRight size={16} />
      </a>
      <a
        href="https://wa.me/225XXXXXXXXXX"
        target="_blank"
        rel="noopener noreferrer"
        class="inline-flex shrink-0 items-center gap-2 rounded-pill border border-paper-100/25 px-5 py-2.5 text-sm font-medium whitespace-nowrap text-paper-50 hover:border-paper-100/50 sm:px-6 sm:py-3"
      >
        <WhatsappLogo size={18} weight="fill" />
        Échanger sur WhatsApp
      </a>
    </div>
  </div>
</section>
