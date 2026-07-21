import { error } from '@sveltejs/kit';
import { ApiError, serverApiGet } from '@iumc/api/server';
import type { PublicArticleDetail } from '$lib/content';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch }) => {
	try {
		const article = await serverApiGet<PublicArticleDetail>(`/articles/${params.slug}`, fetch);
		return { article };
	} catch (exception) {
		if (exception instanceof ApiError && exception.status === 404) {
			error(404, 'Article introuvable');
		}
		throw exception;
	}
};
