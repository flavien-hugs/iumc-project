// Types des contenus servis par l'API publique + mapping des icônes du site
// (les icônes restent une affaire de présentation, hors base de données).

import type { Component } from 'svelte';
import { Newspaper } from 'phosphor-svelte';
import LegalDivisionIcon from '$lib/illustrations/LegalDivisionIcon.svelte';
import RealEstateDivisionIcon from '$lib/illustrations/RealEstateDivisionIcon.svelte';
import AgroDivisionIcon from '$lib/illustrations/AgroDivisionIcon.svelte';

export interface PublicService {
	id: number;
	slug: string;
	title: string;
	summary: string | null;
	description: string | null;
}

export interface PublicDivision {
	id: number;
	slug: string;
	name: string;
	status: 'active' | 'coming_soon';
	short_description: string | null;
	full_description: string | null;
	services: PublicService[];
}

export interface PublicArticleSummary {
	slug: string;
	title: string;
	category: string | null;
	summary: string | null;
	published_at: string | null;
}

export interface PublicArticleDetail extends PublicArticleSummary {
	body: string | null;
	author_name: string | null;
}

export interface PublicFaq {
	question: string;
	answer: string;
	division_id: number | null;
	service_id: number | null;
}

export const LOCATION_STATUS_LABELS: Record<string, string> = {
	headquarters: 'Siège',
	open_branch: 'Agence ouverte',
	representation: 'Représentation',
	opening_in_progress: 'Implantation en cours',
	planned: 'Implantation prévue'
};

type IconComponent = Component<{ class?: string }>;

const DIVISION_ICONS: Record<string, IconComponent> = {
	juridique: LegalDivisionIcon,
	'foncier-immobilier': RealEstateDivisionIcon,
	agropastoral: AgroDivisionIcon
};

export function divisionIcon(slug: string): IconComponent {
	return DIVISION_ICONS[slug] ?? LegalDivisionIcon;
}

export function articleIcon(category: string | null): IconComponent {
	const normalized = (category ?? '').toLowerCase();
	if (/foncier|immobil|acd|terrain/.test(normalized)) return RealEstateDivisionIcon;
	if (/juridique|bail|litige|contrat/.test(normalized)) return LegalDivisionIcon;
	if (/agro|élevage|elevage/.test(normalized)) return AgroDivisionIcon;
	return Newspaper as IconComponent;
}

export function formatPublishedDate(iso: string | null): string {
	if (!iso) return '';
	return new Date(iso).toLocaleDateString('fr-FR', {
		day: 'numeric',
		month: 'long',
		year: 'numeric'
	});
}

/**
 * Version texte brut d'un contenu HTML (éditeur riche du panel), pour les
 * contextes qui ne peuvent pas afficher de balises : meta description, etc.
 */
export function stripHtml(html: string | null): string {
	if (!html) return '';
	return html
		.replace(/<[^>]+>/g, ' ')
		.replace(/\s+/g, ' ')
		.trim();
}
