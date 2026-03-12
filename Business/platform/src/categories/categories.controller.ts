import { Controller, Get, Param, Query } from '@nestjs/common';
import { CategoriesService } from './categories.service';

@Controller('categories')
export class CategoriesController {
  constructor(private categoriesService: CategoriesService) {}

  @Get()
  findAll(@Query('includeInactive') includeInactive?: boolean) {
    return this.categoriesService.findAll(includeInactive);
  }

  @Get(':slug')
  findBySlug(@Param('slug') slug: string) {
    return this.categoriesService.findBySlug(slug);
  }

  @Get(':id/skills')
  getSkills(@Param('id') id: string) {
    return this.categoriesService.getSkills(id);
  }
}
