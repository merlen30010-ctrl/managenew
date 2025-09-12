from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.contract import Contract, ContractFile
from app.models.customer import Customer
from app.models.material import Material
from app.models.department import Department
from app.models.user import User
from app.utils.pagination_service import pagination_service
from sqlalchemy.orm import joinedload
import os
from datetime import datetime
import uuid
import logging
import platform

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加Word转PDF所需库
# 根据操作系统选择合适的库
if platform.system().lower() == 'windows':
    try:
        import comtypes.client
        HAS_COMTYPES = True
        logger.info("成功导入comtypes库（Windows环境）")
    except ImportError:
        HAS_COMTYPES = False
        logger.warning("未能导入comtypes库")
else:
    HAS_COMTYPES = False
    logger.info("非Windows环境，跳过comtypes库导入")

try:
    import subprocess
    HAS_SUBPROCESS = True
    logger.info("成功导入subprocess库")
except ImportError:
    HAS_SUBPROCESS = False
    logger.warning("未能导入subprocess库")

try:
    from docxtopdf import convert as docx_convert
    HAS_DOCTOPDF = True
    logger.info("成功导入docxtopdf库")
except ImportError:
    HAS_DOCTOPDF = False
    logger.warning("未能导入docxtopdf库")

# 检查系统中是否安装了libreoffice
HAS_LIBREOFFICE = False
if HAS_SUBPROCESS:
    try:
        result = subprocess.run(['which', 'libreoffice'], capture_output=True, text=True)
        if result.returncode == 0:
            HAS_LIBREOFFICE = True
            logger.info("系统中检测到libreoffice")
        else:
            logger.info("系统中未检测到libreoffice")
    except Exception as e:
        logger.warning(f"检查libreoffice时出错: {e}")

contract_bp = Blueprint('contract', __name__)

def convert_word_to_pdf(word_path, pdf_path):
    """
    将Word文档转换为PDF（跨平台实现）
    """
    logger.info(f"开始转换Word文档: {word_path} -> {pdf_path}")
    logger.info(f"运行环境: {platform.system()}")
    
    # 确保路径是绝对路径
    word_path = os.path.abspath(word_path)
    pdf_path = os.path.abspath(pdf_path)
    
    logger.info(f"绝对路径: {word_path} -> {pdf_path}")
    
    # 检查源文件是否存在
    if not os.path.exists(word_path):
        logger.error(f"源文件不存在: {word_path}")
        return False
    
    # 确保目标目录存在
    pdf_dir = os.path.dirname(pdf_path)
    os.makedirs(pdf_dir, exist_ok=True)
    
    logger.info(f"目标目录: {pdf_dir}")
    
    # Windows环境下优先使用comtypes
    if platform.system().lower() == 'windows' and HAS_COMTYPES:
        try:
            logger.info("使用comtypes转换Word文档（Windows环境）")
            
            # 初始化Word应用程序
            word = comtypes.client.CreateObject('Word.Application')
            word.Visible = False
            
            # 打开文档
            logger.info(f"打开文档: {word_path}")
            doc = word.Documents.Open(word_path)
            
            # 保存为PDF
            logger.info(f"保存为PDF: {pdf_path}")
            doc.SaveAs(pdf_path, FileFormat=17)  # 17表示PDF格式
            
            # 关闭文档和应用程序
            doc.Close()
            word.Quit()
            
            # 检查PDF文件是否创建成功
            if os.path.exists(pdf_path):
                logger.info(f"成功使用comtypes转换Word文档为PDF: {pdf_path}")
                return True
            else:
                logger.error("PDF文件未创建成功")
                return False
                
        except Exception as e:
            logger.error(f"使用Word应用程序转换失败: {e}")
            try:
                word.Quit()
            except:
                pass
            # 继续尝试其他方法
    
    # Linux/Mac环境下优先使用libreoffice
    if HAS_LIBREOFFICE:
        try:
            logger.info("使用libreoffice转换Word文档")
            
            # 使用libreoffice命令行工具转换
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', pdf_dir,
                word_path
            ]
            
            logger.info(f"执行命令: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info("使用libreoffice转换成功")
                # libreoffice会自动创建PDF文件，文件名与原文件相同但扩展名不同
                # 我们需要检查文件是否已经存在
                if os.path.exists(pdf_path):
                    logger.info(f"PDF文件已存在: {pdf_path}")
                    return True
                else:
                    # 如果文件名不匹配，尝试查找生成的PDF文件
                    base_name = os.path.splitext(os.path.basename(word_path))[0]
                    generated_pdf = os.path.join(pdf_dir, f"{base_name}.pdf")
                    if os.path.exists(generated_pdf):
                        # 重命名文件以匹配我们的命名规则
                        os.rename(generated_pdf, pdf_path)
                        logger.info(f"重命名PDF文件: {generated_pdf} -> {pdf_path}")
                        return True
                    else:
                        logger.error(f"未找到生成的PDF文件: {generated_pdf}")
                        return False
            else:
                logger.error(f"libreoffice转换失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("libreoffice转换超时")
            return False
        except Exception as e:
            logger.error(f"使用libreoffice转换失败: {e}")
    
    # 如果libreoffice不可用，尝试使用docxtopdf
    if HAS_DOCTOPDF:
        try:
            logger.info(f"使用docxtopdf转换Word文档: {word_path}")
            docx_convert(word_path, pdf_path)
            
            # 检查PDF文件是否创建成功
            if os.path.exists(pdf_path):
                logger.info(f"成功使用docxtopdf转换Word文档为PDF: {pdf_path}")
                return True
            else:
                logger.error("PDF文件未创建成功")
                return False
                
        except Exception as e:
            logger.error(f"使用docxtopdf转换失败: {e}")
    
    logger.error("所有转换方法都失败了")
    return False

@contract_bp.route('/')
@login_required
def list_contracts():
    # 使用eager loading预加载关联对象
    query = Contract.query.options(
        joinedload(Contract.customer),
        joinedload(Contract.material),
        joinedload(Contract.factory),
        joinedload(Contract.responsible)
    )
    
    # 使用分页服务
    pagination_result = pagination_service.paginate_query(
        query,
        Contract,
        default_sort='created_at',
        allowed_sorts=['created_at', 'sign_date', 'expiry_date', 'contract_number']
    )
    
    return render_template('contracts/list.html', 
                         contracts=pagination_result['items'],
                         pagination=pagination_result)

@contract_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_contract():
    if request.method == 'POST':
        contract_type = request.form.get('contract_type')
        contract_number = request.form.get('contract_number')
        customer_id = request.form.get('customer_id')
        material_id = request.form.get('material_id')
        factory_id = request.form.get('factory_id')
        responsible_id = request.form.get('responsible_id')
        sign_date = request.form.get('sign_date')
        expiry_date = request.form.get('expiry_date')
        tax_rate = request.form.get('tax_rate') or 0
        pricing_method = request.form.get('pricing_method')
        coefficient = request.form.get('coefficient')
        status = request.form.get('status') or '草稿'
        # 读取布尔字段
        is_tax_inclusive = request.form.get('is_tax_inclusive') == 'on'
        is_invoice_received = request.form.get('is_invoice_received') == 'on'
        
        # 检查合同编号是否已存在
        if Contract.query.filter_by(contract_number=contract_number).first():
            flash('合同编号已存在')
            return redirect(url_for('contract.create_contract'))
        
        # 创建新合同
        contract = Contract(
            contract_type=contract_type,
            contract_number=contract_number,
            customer_id=int(customer_id),
            material_id=int(material_id),
            factory_id=int(factory_id),
            responsible_id=int(responsible_id),
            sign_date=datetime.strptime(sign_date, '%Y-%m-%d').date() if sign_date else None,
            expiry_date=datetime.strptime(expiry_date, '%Y-%m-%d').date() if expiry_date else None,
            tax_rate=float(tax_rate),
            pricing_method=pricing_method,
            coefficient=float(coefficient) if coefficient else None,
            status=status,
            is_tax_inclusive=is_tax_inclusive,
            is_invoice_received=is_invoice_received
        )
        
        db.session.add(contract)
        db.session.commit()
        
        # 处理文件上传
        file = request.files.get('file')
        if file and file.filename:
            try:
                logger.info(f"开始处理文件上传: {file.filename}")
                
                # 创建上传目录
                upload_dir = os.path.join('uploads', 'contract', datetime.now().strftime('%Y%m'))
                os.makedirs(upload_dir, exist_ok=True)
                logger.info(f"上传目录: {upload_dir}")
                
                # 生成文件名：客户名+物料名+时间戳+扩展名
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                customer = Customer.query.get(contract.customer_id)
                material = Material.query.get(contract.material_id)
                filename_base = f"{customer.name}_{material.name}_{timestamp}"
                file_ext = os.path.splitext(file.filename)[1]
                file_path = os.path.join(upload_dir, f"{filename_base}{file_ext}")
                
                # 保存文件
                file.save(file_path)
                logger.info(f"文件保存成功: {file_path}")
                
                # 检查文件是否保存成功
                if not os.path.exists(file_path):
                    logger.error(f"文件保存失败: {file_path}")
                    flash('合同创建成功，但文件保存失败')
                    return redirect(url_for('contract.list_contracts'))
                
                # 如果是Word文档，转换为PDF
                pdf_file_path = None
                if file_ext.lower() in ['.doc', '.docx']:
                    logger.info(f"检测到Word文档，开始转换为PDF: {file.filename}")
                    try:
                        pdf_filename = f"{filename_base}.pdf"
                        pdf_file_path = os.path.join(upload_dir, pdf_filename)
                        logger.info(f"PDF目标路径: {pdf_file_path}")
                        
                        success = convert_word_to_pdf(file_path, pdf_file_path)
                        if success and os.path.exists(pdf_file_path):
                            logger.info(f"Word文档转换PDF成功: {pdf_file_path}")
                        else:
                            pdf_file_path = None
                            logger.warning(f"Word文档转换PDF失败: {file_path}")
                    except Exception as e:
                        logger.error(f"转换Word到PDF时出错: {e}")
                        pdf_file_path = None
                
                # 创建合同文件记录
                contract_file = ContractFile(
                    contract_id=contract.id,
                    file_path=file_path,
                    file_name=file.filename,
                    file_type=file_ext.lower()
                )
                
                db.session.add(contract_file)
                db.session.commit()
                logger.info(f"合同文件记录创建成功: {file.filename}")
                
                # 如果成功生成了PDF，也创建PDF文件记录
                if pdf_file_path and os.path.exists(pdf_file_path):
                    pdf_contract_file = ContractFile(
                        contract_id=contract.id,
                        file_path=pdf_file_path,
                        file_name=f"{filename_base}.pdf",
                        file_type='.pdf'
                    )
                    db.session.add(pdf_contract_file)
                    db.session.commit()
                    logger.info(f"PDF文件记录创建成功: {pdf_file_path}")
                    flash('合同创建成功，文件上传并转换为PDF成功')
                else:
                    flash('合同创建成功，文件上传成功')
                    
            except Exception as e:
                logger.error(f"文件上传处理过程中出错: {e}")
                flash('合同创建成功，但文件上传失败')
        else:
            flash('合同创建成功')
        
        return redirect(url_for('contract.list_contracts'))
    
    # 获取下拉选项数据
    customers = Customer.query.all()
    materials = Material.query.all()
    factories = Department.query.filter_by(level=1).all()  # 只获取分厂
    users = User.query.all()  # 获取所有用户作为负责人选项
    
    return render_template('contracts/create.html', 
                         customers=customers, 
                         materials=materials, 
                         factories=factories, 
                         users=users)

@contract_bp.route('/<int:contract_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    
    if request.method == 'POST':
        # 若合同已归档且非超级管理员，禁止编辑
        if contract.status == '合同归档' and not current_user.is_superuser:
            flash('合同已归档，只有超级管理员可以编辑。')
            return redirect(url_for('contract.list_contracts'))
        
        contract.contract_type = request.form.get('contract_type')
        contract.contract_number = request.form.get('contract_number')
        contract.customer_id = int(request.form.get('customer_id'))
        contract.material_id = int(request.form.get('material_id'))
        contract.factory_id = int(request.form.get('factory_id'))
        contract.responsible_id = int(request.form.get('responsible_id'))
        sign_date = request.form.get('sign_date')
        expiry_date = request.form.get('expiry_date')
        contract.tax_rate = float(request.form.get('tax_rate') or 0)
        contract.pricing_method = request.form.get('pricing_method')
        coefficient = request.form.get('coefficient')
        contract.coefficient = float(coefficient) if coefficient else None
        contract.status = request.form.get('status') or '执行'
        # 读取布尔字段
        contract.is_tax_inclusive = request.form.get('is_tax_inclusive') == 'on'
        contract.is_invoice_received = request.form.get('is_invoice_received') == 'on'
        
        contract.sign_date = datetime.strptime(sign_date, '%Y-%m-%d').date() if sign_date else None
        contract.expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date() if expiry_date else None
        
        db.session.commit()
        flash('合同信息更新成功')
        return redirect(url_for('contract.list_contracts'))
    
    # 获取下拉选项数据
    customers = Customer.query.all()
    materials = Material.query.all()
    factories = Department.query.filter_by(level=1).all()  # 只获取分厂
    users = User.query.all()  # 获取所有用户作为负责人选项
    
    return render_template('contracts/edit.html', 
                         contract=contract,
                         customers=customers, 
                         materials=materials, 
                         factories=factories, 
                         users=users)

@contract_bp.route('/<int:contract_id>/upload', methods=['GET', 'POST'])
@login_required
def upload_contract_file(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    
    if request.method == 'POST':
        # 若合同已归档且非超级管理员，禁止上传附件
        if contract.status == '合同归档' and not current_user.is_superuser:
            flash('合同已归档，只有超级管理员可以上传或删除附件。')
            return render_template('contracts/upload.html', contract=contract)
        file = request.files.get('file')
        if file and file.filename:
            try:
                # 创建上传目录
                upload_dir = os.path.join('uploads', 'contract', datetime.now().strftime('%Y%m'))
                os.makedirs(upload_dir, exist_ok=True)
                
                # 生成文件名：客户名+物料名+时间戳+扩展名
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                customer = Customer.query.get(contract.customer_id)
                material = Material.query.get(contract.material_id)
                filename_base = f"{customer.name}_{material.name}_{timestamp}"
                file_ext = os.path.splitext(file.filename)[1]
                file_path = os.path.join(upload_dir, f"{filename_base}{file_ext}")
                
                # 保存文件
                file.save(file_path)
                logger.info(f"文件保存成功: {file_path}")
                
                # 如果是Word文档，转换为PDF
                pdf_file_path = None
                if file_ext.lower() in ['.doc', '.docx']:
                    logger.info(f"检测到Word文档，开始转换为PDF: {file.filename}")
                    try:
                        pdf_filename = f"{filename_base}.pdf"
                        pdf_file_path = os.path.join(upload_dir, pdf_filename)
                        success = convert_word_to_pdf(file_path, pdf_file_path)
                        if success and os.path.exists(pdf_file_path):
                            logger.info(f"Word文档转换PDF成功: {pdf_file_path}")
                        else:
                            pdf_file_path = None
                            logger.warning(f"Word文档转换PDF失败: {file_path}")
                    except Exception as e:
                        logger.error(f"转换Word到PDF时出错: {e}")
                        pdf_file_path = None
                
                # 创建合同文件记录
                contract_file = ContractFile(
                    contract_id=contract.id,
                    file_path=file_path,
                    file_name=file.filename,
                    file_type=file_ext.lower()
                )
                
                db.session.add(contract_file)
                db.session.commit()
                logger.info(f"合同文件记录创建成功: {file.filename}")
                
                # 如果成功生成了PDF，也创建PDF文件记录
                if pdf_file_path and os.path.exists(pdf_file_path):
                    pdf_contract_file = ContractFile(
                        contract_id=contract.id,
                        file_path=pdf_file_path,
                        file_name=f"{filename_base}.pdf",
                        file_type='.pdf'
                    )
                    db.session.add(pdf_contract_file)
                    db.session.commit()
                    logger.info(f"PDF文件记录创建成功: {pdf_file_path}")
                    flash('文件上传并转换为PDF成功')
                else:
                    flash('文件上传成功')
                    
            except Exception as e:
                logger.error(f"文件上传处理过程中出错: {e}")
                flash('文件上传失败')
        else:
            flash('请选择要上传的文件')
    
    return render_template('contracts/upload.html', contract=contract)

@contract_bp.route('/file/<int:file_id>/download')
@login_required
def download_contract_file(file_id):
    try:
        # 获取文件记录
        contract_file = ContractFile.query.get_or_404(file_id)
        
        # 验证文件记录
        if not contract_file.file_path:
            logger.error(f"文件记录中缺少文件路径: {file_id}")
            flash('文件路径信息不完整')
            return redirect(url_for('contract.list_contracts'))
        
        # 使用os.path.abspath获取绝对路径
        file_path = os.path.abspath(contract_file.file_path)
        logger.info(f"尝试下载文件: {file_path}")
        
        # 检查文件是否存在
        if os.path.exists(file_path):
            # 验证路径安全性（防止路径遍历攻击）
            if not os.path.commonpath([os.path.abspath(''), file_path]).startswith(os.path.abspath('')):
                logger.error(f"文件路径不安全: {file_path}")
                flash('文件路径不安全')
                return redirect(url_for('contract.list_contracts'))
            
            from flask import send_file
            # 使用os.path.basename获取文件名，确保跨平台兼容性
            filename = os.path.basename(file_path)
            logger.info(f"文件存在，准备下载: {filename}")
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            logger.error(f"文件不存在: {file_path}")
            flash(f'文件不存在: {contract_file.file_name}')
            return redirect(url_for('contract.list_contracts'))
            
    except Exception as e:
        logger.error(f"下载文件时发生错误: {str(e)}")
        flash(f'下载文件时发生错误: {str(e)}')
        return redirect(url_for('contract.list_contracts'))

@contract_bp.route('/file/<int:file_id>/preview')
@login_required
def preview_contract_file(file_id):
    try:
        # 获取文件记录
        contract_file = ContractFile.query.get_or_404(file_id)
        
        # 验证文件记录
        if not contract_file.file_path:
            logger.error(f"文件记录中缺少文件路径: {file_id}")
            flash('文件路径信息不完整')
            return redirect(url_for('contract.list_contracts'))
        
        # 使用os.path.abspath获取绝对路径
        file_path = os.path.abspath(contract_file.file_path)
        logger.info(f"尝试预览文件: {file_path}")
        
        # 检查文件是否存在
        if os.path.exists(file_path):
            # 验证路径安全性（防止路径遍历攻击）
            if not os.path.commonpath([os.path.abspath(''), file_path]).startswith(os.path.abspath('')):
                logger.error(f"文件路径不安全: {file_path}")
                flash('文件路径不安全')
                return redirect(url_for('contract.list_contracts'))
            
            # 获取文件扩展名（使用os.path.splitext确保兼容性）
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # 根据文件类型设置MIME类型
            mime_types = {
                '.pdf': 'application/pdf',
                '.txt': 'text/plain',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif'
            }
            
            # 如果是PDF或图片文件，直接显示
            if file_ext in mime_types:
                from flask import send_file
                logger.info(f"预览文件类型: {file_ext}")
                return send_file(file_path, as_attachment=False, mimetype=mime_types[file_ext])
            # 如果是Word文档，检查是否有对应的PDF版本
            elif file_ext in ['.doc', '.docx']:
                logger.info("检测到Word文档，查找对应的PDF版本")
                # 查找是否有对应的PDF文件
                pdf_file = ContractFile.query.filter_by(
                    contract_id=contract_file.contract_id,
                    file_type='.pdf'
                ).first()
                
                if pdf_file:
                    # 检查PDF文件是否存在
                    pdf_path = os.path.abspath(pdf_file.file_path)
                    if os.path.exists(pdf_path):
                        # 验证PDF路径安全性
                        if not os.path.commonpath([os.path.abspath(''), pdf_path]).startswith(os.path.abspath('')):
                            logger.error(f"PDF文件路径不安全: {pdf_path}")
                            flash('PDF文件路径不安全')
                            return redirect(url_for('contract.list_contracts'))
                        
                        from flask import send_file
                        logger.info(f"预览对应的PDF文件: {pdf_path}")
                        return send_file(pdf_path, as_attachment=False, mimetype='application/pdf')
                    else:
                        logger.error(f"PDF文件不存在: {pdf_path}")
                        flash('对应的PDF文件不存在')
                        return redirect(url_for('contract.list_contracts'))
                else:
                    logger.warning("未找到对应的PDF文件")
                    flash('该文件类型需要转换为PDF才能预览')
                    return redirect(url_for('contract.list_contracts'))
            else:
                logger.warning(f"不支持预览的文件类型: {file_ext}")
                flash('该文件类型不支持预览')
                return redirect(url_for('contract.list_contracts'))
        else:
            logger.error(f"文件不存在: {file_path}")
            flash(f'文件不存在: {contract_file.file_name}')
            return redirect(url_for('contract.list_contracts'))
            
    except Exception as e:
        logger.error(f"预览文件时发生错误: {str(e)}")
        flash(f'预览文件时发生错误: {str(e)}')
        return redirect(url_for('contract.list_contracts'))

@contract_bp.route('/file/<int:file_id>/delete', methods=['POST'])
@login_required
def delete_contract_file(file_id):
    try:
        contract_file = ContractFile.query.get_or_404(file_id)
        # 取关联合同并检查归档
        contract = Contract.query.get(contract_file.contract_id)
        if contract and contract.status == '合同归档' and not current_user.is_superuser:
            flash('合同已归档，只有超级管理员可以删除附件。')
            return redirect(url_for('contract.list_contracts'))
        
        # 验证文件记录
        if not contract_file.file_path:
            logger.error(f"文件记录中缺少文件路径: {file_id}")
            flash('文件路径信息不完整')
            return redirect(url_for('contract.list_contracts'))
        
        # 使用os.path.abspath获取绝对路径
        file_path = os.path.abspath(contract_file.file_path)
        logger.info(f"尝试删除文件: {file_path}")
        
        # 删除文件系统中的文件
        if os.path.exists(file_path):
            try:
                # 验证路径安全性
                if not os.path.commonpath([os.path.abspath(''), file_path]).startswith(os.path.abspath('')):
                    logger.error(f"文件路径不安全: {file_path}")
                    flash('文件路径不安全')
                    return redirect(url_for('contract.list_contracts'))
                
                os.remove(file_path)
                logger.info(f"文件删除成功: {file_path}")
            except PermissionError:
                logger.error(f"没有权限删除文件: {file_path}")
                flash(f'没有权限删除文件: {contract_file.file_name}')
                return redirect(url_for('contract.list_contracts'))
            except Exception as e:
                logger.error(f"文件删除失败: {str(e)}")
                flash(f'文件删除失败: {str(e)}')
                return redirect(url_for('contract.list_contracts'))
        else:
            logger.warning(f"文件不存在，跳过删除: {file_path}")
        
        db.session.delete(contract_file)
        db.session.commit()
        logger.info("数据库记录删除成功")
        flash('文件删除成功')
        return redirect(url_for('contract.list_contracts'))
        
    except Exception as e:
        logger.error(f"删除文件时发生错误: {str(e)}")
        flash(f'删除文件时发生错误: {str(e)}')
        return redirect(url_for('contract.list_contracts'))

@contract_bp.route('/<int:contract_id>/delete', methods=['POST'])
@login_required
def delete_contract(contract_id):
    try:
        contract = Contract.query.get_or_404(contract_id)
        # 若合同已归档且非超级管理员，禁止删除
        if contract.status == '合同归档' and not current_user.is_superuser:
            flash('合同已归档，只有超级管理员可以删除合同。')
            return redirect(url_for('contract.list_contracts'))
        
        # 删除关联的合同文件
        for file in contract.files:
            try:
                # 验证文件记录
                if not file.file_path:
                    logger.warning(f"文件记录中缺少文件路径: {file.id}")
                    continue
                
                # 使用os.path.abspath获取绝对路径
                file_path = os.path.abspath(file.file_path)
                logger.info(f"尝试删除合同关联文件: {file_path}")
                
                # 删除文件系统中的文件
                if os.path.exists(file_path):
                    try:
                        # 验证路径安全性
                        if not os.path.commonpath([os.path.abspath(''), file_path]).startswith(os.path.abspath('')):
                            logger.error(f"文件路径不安全: {file_path}")
                            continue
                            
                        os.remove(file_path)
                        logger.info(f"合同关联文件删除成功: {file_path}")
                    except PermissionError:
                        logger.error(f"没有权限删除文件: {file_path}")
                    except Exception as e:
                        logger.error(f"合同关联文件删除失败: {str(e)}")
                else:
                    logger.warning(f"合同关联文件不存在，跳过删除: {file_path}")
            except Exception as e:
                logger.error(f"处理合同关联文件时发生错误: {str(e)}")
            
            db.session.delete(file)
        
        db.session.delete(contract)
        db.session.commit()
        logger.info(f"合同删除成功: {contract_id}")
        flash('合同删除成功')
        return redirect(url_for('contract.list_contracts'))
        
    except Exception as e:
        logger.error(f"删除合同时发生错误: {str(e)}")
        flash(f'删除合同时发生错误: {str(e)}')
        return redirect(url_for('contract.list_contracts'))


