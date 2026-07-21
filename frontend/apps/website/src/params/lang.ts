import type { ParamMatcher } from '@sveltejs/kit';

/**
 * Langues supportées. Seul le français est livré au MVP (PRD/CDC) ; la
 * structure de routes anticipe l'ajout futur de l'anglais (ADR-0009).
 */
export const SUPPORTED_LANGS = ['fr'] as const;

export const match: ParamMatcher = (param) => {
	return (SUPPORTED_LANGS as readonly string[]).includes(param);
};
