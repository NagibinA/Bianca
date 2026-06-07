"""API views for Bianca integration."""

import json
from aiohttp import web
from homeassistant.components.http import HomeAssistantView

from .const import DOMAIN
from . import get_program_manager


class BiancaAddProgramFullView(HomeAssistantView):
    """Эндпоинт для добавления программы со всеми опциями и взаимоисключениями."""
    
    url = "/api/bianca/add_program_full"
    name = "api:bianca:add_program_full"
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()
        
        name = data.get("name")
        pr = data.get("Pr")
        pr_code = data.get("PrCode")
        pr_str = data.get("PrStr")
        pr_str_raw = data.get("PrStrRaw", "")
        options = data.get("options", {})
        mutual_exclusion = data.get("mutual_exclusion", [])
        
        if not all([name, pr, pr_code, pr_str]):
            return web.json_response(
                {"success": False, "error": "Не все поля заполнены"},
                status=400
            )
        
        program_manager = get_program_manager(hass)
        if not program_manager:
            return web.json_response(
                {"success": False, "error": "Интеграция Bianca не найдена"},
                status=404
            )
        
        prog_id = program_manager.add_program(name, pr, pr_code, pr_str, pr_str_raw, options, mutual_exclusion)
        
        return web.json_response({
            "success": True,
            "message": f"Программа '{name}' (ID: {prog_id}) добавлена! Перезапустите Home Assistant.",
            "program_id": prog_id
        })


class BiancaAddMultipleProgramsView(HomeAssistantView):
    """Эндпоинт для массового добавления программ."""
    
    url = "/api/bianca/add_multiple_programs"
    name = "api:bianca:add_multiple_programs"
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()
        
        program_manager = get_program_manager(hass)
        if not program_manager:
            return web.json_response(
                {"success": False, "error": "Интеграция Bianca не найдена"},
                status=404
            )
        
        # Извлекаем список программ из разных форматов
        programs_to_add = []
        
        if "programs" in data:
            if isinstance(data["programs"], dict):
                for prog_data in data["programs"].values():
                    programs_to_add.append(prog_data)
            elif isinstance(data["programs"], list):
                programs_to_add = data["programs"]
        else:
            if "name" in data and "Pr" in data:
                programs_to_add = [data]
        
        if not programs_to_add:
            return web.json_response({
                "success": False,
                "error": "Не найден список программ в запросе"
            }, status=400)
        
        added = []
        skipped = []
        errors = []
        
        for prog in programs_to_add:
            name = prog.get("name")
            pr = prog.get("Pr")
            pr_code = prog.get("PrCode", 0)
            pr_str = prog.get("PrStr", "")
            pr_str_raw = prog.get("PrStrRaw", pr_str)
            options = prog.get("options", {})
            mutual_exclusion = prog.get("mutual_exclusion", [])
            
            if not name or pr is None:
                errors.append(f"Пропущена программа: нет name или Pr")
                continue
            
            try:
                program_manager.add_program(name, pr, pr_code, pr_str, pr_str_raw, options, mutual_exclusion)
                added.append(f"{pr} - {name}")
            except Exception as e:
                errors.append(f"{pr} - {name}: {e}")
        
        program_manager._save_config()
        
        return web.json_response({
            "success": True,
            "added": added,
            "skipped": skipped,
            "errors": errors,
            "message": f"Добавлено: {len(added)}, Пропущено: {len(skipped)}, Ошибок: {len(errors)}"
        })


class BiancaGetProgramsView(HomeAssistantView):
    """Эндпоинт для получения списка программ."""
    
    url = "/api/bianca/get_programs"
    name = "api:bianca:get_programs"
    requires_auth = False

    async def get(self, request):
        hass = request.app["hass"]
        
        program_manager = get_program_manager(hass)
        if not program_manager:
            return web.json_response({"success": False, "error": "Интеграция Bianca не найдена"}, status=404)
        
        programs_list = []
        for prog_id, prog in program_manager.programs.items():
            programs_list.append({
                "id": int(prog_id),
                "name": prog.get("name", ""),
                "Pr": prog.get("Pr", 0),
                "PrCode": prog.get("PrCode", 0),
                "PrStr": prog.get("PrStr", ""),
                "PrStrRaw": prog.get("PrStrRaw", ""),
            })
        
        return web.json_response({"success": True, "programs": programs_list, "next_id": program_manager.next_id})


class BiancaGetProgramView(HomeAssistantView):
    """Эндпоинт для получения полной информации о программе."""
    
    url = "/api/bianca/get_program/{program_id}"
    name = "api:bianca:get_program"
    requires_auth = False

    async def get(self, request, program_id):
        hass = request.app["hass"]
        
        program_manager = get_program_manager(hass)
        if not program_manager:
            return web.json_response({"success": False, "error": "Интеграция Bianca не найдена"}, status=404)
        
        program = program_manager.get_program(int(program_id))
        if not program:
            return web.json_response({"success": False, "error": f"Program {program_id} not found"}, status=404)
        
        return web.json_response({
            "success": True,
            "program": {
                "id": int(program_id),
                "name": program.get("name", ""),
                "Pr": program.get("Pr", 0),
                "PrCode": program.get("PrCode", 0),
                "PrStr": program.get("PrStr", ""),
                "PrStrRaw": program.get("PrStrRaw", ""),
                "options": program.get("options", {}),
                "mutual_exclusion": program.get("mutual_exclusion", [])
            }
        })


class BiancaUpdateProgramView(HomeAssistantView):
    """Эндпоинт для обновления программы."""
    
    url = "/api/bianca/update_program"
    name = "api:bianca:update_program"
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()
        
        program_id = data.get("program_id")
        name = data.get("name")
        pr = data.get("Pr")
        pr_code = data.get("PrCode")
        pr_str = data.get("PrStr")
        pr_str_raw = data.get("PrStrRaw", "")
        options = data.get("options", {})
        mutual_exclusion = data.get("mutual_exclusion", [])
        
        if not all([program_id, name, pr, pr_code, pr_str]):
            return web.json_response(
                {"success": False, "error": "Не все поля заполнены"},
                status=400
            )
        
        program_manager = get_program_manager(hass)
        if not program_manager:
            return web.json_response({"success": False, "error": "Интеграция Bianca не найдена"}, status=404)
        
        success = program_manager.update_program(program_id, name, pr, pr_code, pr_str, pr_str_raw, options, mutual_exclusion)
        
        if not success:
            return web.json_response({"success": False, "error": "Program not found"}, status=404)
        
        return web.json_response({
            "success": True,
            "message": f"Программа '{name}' обновлена! Перезапустите Home Assistant."
        })


class BiancaDeleteProgramView(HomeAssistantView):
    """Эндпоинт для удаления программы."""
    
    url = "/api/bianca/delete_program"
    name = "api:bianca:delete_program"
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()
        
        program_id = data.get("program_id")
        
        if not program_id:
            return web.json_response(
                {"success": False, "error": "ID программы не указан"},
                status=400
            )
        
        program_manager = get_program_manager(hass)
        if not program_manager:
            return web.json_response({"success": False, "error": "Интеграция Bianca не найдена"}, status=404)
        
        program = program_manager.get_program(program_id)
        if not program:
            return web.json_response({"success": False, "error": f"Программа с ID {program_id} не найдена"}, status=404)
        
        program_name = program.get("name", program_id)
        program_manager.delete_program(program_id)
        
        return web.json_response({
            "success": True,
            "message": f"Программа '{program_name}' удалена! Перезапустите Home Assistant."
        })


async def async_register_views(hass):
    """Register API views."""
    hass.http.register_view(BiancaAddProgramFullView)
    hass.http.register_view(BiancaAddMultipleProgramsView)
    hass.http.register_view(BiancaGetProgramsView)
    hass.http.register_view(BiancaGetProgramView)
    hass.http.register_view(BiancaUpdateProgramView)
    hass.http.register_view(BiancaDeleteProgramView)
    _LOGGER.info("Bianca API views registered")