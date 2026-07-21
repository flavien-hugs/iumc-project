import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, parent }) => {
	const { divisions } = await parent();
	const division = divisions.find((item) => item.slug === params.division);
	if (!division) {
		error(404, 'Pôle introuvable');
	}
	return { division };
};
