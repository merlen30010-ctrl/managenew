# 物料管理相关API路由
from flask import Blueprint, jsonify, request
from app import db
from app.models.material import Material
from app.api.decorators import api_login_required, permission_required
import logging

# 创建物料API蓝图
api_material_bp = Blueprint('api_material', __name__, url_prefix='/api')

# 配置日志
logger = logging.getLogger(__name__)

@api_material_bp.route('/materials', methods=['GET'])
@api_login_required
@permission_required('material_read')
def get_materials():
    """获取物料列表"""
    try:
        materials = Material.query.all()
        return jsonify({
            'success': True,
            'data': [{
                'id': material.id,
                'name': material.name,
                'code': material.code,
                'full_name': material.full_name,
                'purpose': material.purpose
            } for material in materials]
        })
    except Exception as e:
        logger.error(f"获取物料列表时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取物料列表失败: {str(e)}'
        }), 500

@api_material_bp.route('/materials/<int:material_id>', methods=['GET'])
@api_login_required
@permission_required('material_read')
def get_material(material_id):
    """获取指定物料信息"""
    try:
        material = Material.query.get_or_404(material_id)
        return jsonify({
            'success': True,
            'data': {
                'id': material.id,
                'name': material.name,
                'code': material.code,
                'full_name': material.full_name,
                'purpose': material.purpose
            }
        })
    except Exception as e:
        logger.error(f"获取物料信息时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取物料信息失败: {str(e)}'
        }), 500

@api_material_bp.route('/materials', methods=['POST'])
@api_login_required
@permission_required('material_create')
def create_material():
    """创建新物料"""
    try:
        data = request.get_json()
        
        # 检查必填字段
        if not data or not data.get('name') or not data.get('code'):
            return jsonify({
                'success': False,
                'message': '物料名称和代码是必填字段'
            }), 400
        
        # 检查物料代码是否已存在
        if Material.query.filter_by(code=data['code']).first():
            return jsonify({
                'success': False,
                'message': '物料代码已存在'
            }), 400
        
        # 创建新物料
        material = Material(
            name=data['name'],
            code=data['code'],
            full_name=data.get('full_name', ''),
            purpose=data.get('purpose', '其他')
        )
        
        db.session.add(material)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '物料创建成功',
            'data': {
                'id': material.id,
                'name': material.name,
                'code': material.code,
                'full_name': material.full_name,
                'purpose': material.purpose
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建物料时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'创建物料失败: {str(e)}'
        }), 500

@api_material_bp.route('/materials/<int:material_id>', methods=['PUT'])
@api_login_required
@permission_required('material_update')
def update_material(material_id):
    """更新物料信息"""
    try:
        material = Material.query.get_or_404(material_id)
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '没有提供更新数据'
            }), 400
        
        # 更新物料信息
        if 'name' in data:
            material.name = data['name']
        
        if 'code' in data:
            # 检查物料代码是否已存在
            existing_material = Material.query.filter_by(code=data['code']).first()
            if existing_material and existing_material.id != material_id:
                return jsonify({
                    'success': False,
                    'message': '物料代码已存在'
                }), 400
            material.code = data['code']
        
        if 'full_name' in data:
            material.full_name = data['full_name']
        
        if 'purpose' in data:
            material.purpose = data['purpose']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '物料更新成功',
            'data': {
                'id': material.id,
                'name': material.name,
                'code': material.code,
                'full_name': material.full_name,
                'purpose': material.purpose
            }
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新物料时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'更新物料失败: {str(e)}'
        }), 500

@api_material_bp.route('/materials/<int:material_id>', methods=['DELETE'])
@api_login_required
@permission_required('material_delete')
def delete_material(material_id):
    """删除物料"""
    try:
        material = Material.query.get_or_404(material_id)
        
        db.session.delete(material)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '物料删除成功'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除物料时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'删除物料失败: {str(e)}'
        }), 500