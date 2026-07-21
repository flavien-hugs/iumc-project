import { serverApiGet } from '@iumc/api/server';
import type { PublicArticleSummary, PublicDivision } from '$lib/content';
import type { RequestHandler } from './$types';

// URLs statiques du site public (PRD section 16). Les pages du panel et les
// pages légales sans contenu validé (mentions légales) sont volontairement
// exclues jusqu'à leur mise en ligne.
const STATIC_PATHS = [
	'',
	'/qui-sommes-nous',
	'/services',
	'/implantations',
	'/actualites',
	'/faq',
	'/contact',
	'/demande'
];

function urlEntry(origin: string, path: string): string {
	return `\t<url>\n\t\t<loc>${origin}/fr${path}</loc>\n\t</url>`;
}

export const GET: RequestHandler = async ({ url, fetch }) => {
	const origin = url.origin;

	const [divisions, articles] = await Promise.all([
		serverApiGet<PublicDivision[]>('/divisions', fetch),
		serverApiGet<PublicArticleSummary[]>('/articles?limit=50', fetch)
	]);

	const entries = [
		...STATIC_PATHS.map((path) => urlEntry(origin, path)),
		...divisions.map((division) => urlEntry(origin, `/services/${division.slug}`)),
		...divisions.flatMap((division) =>
			division.services.map((service) =>
				urlEntry(origin, `/services/${division.slug}/${service.slug}`)
			)
		),
		...articles.map((article) => urlEntry(origin, `/actualites/${article.slug}`))
	];

	const body = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${entries.join('\n')}\n</urlset>\n`;

	return new Response(body, {
		headers: {
			'Content-Type': 'application/xml',
			'Cache-Control': 'max-age=3600'
		}
	});
};
