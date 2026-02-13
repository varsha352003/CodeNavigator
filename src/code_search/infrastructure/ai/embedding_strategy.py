"""Strategy for generating embedding text for code elements."""

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.models.file_models import FileIndex
    from ...domain.models.code_models import CodeMember, CodeMethod


class EmbeddingStrategy:
    """Generates short, name-first embedding text for code elements."""

    @staticmethod
    def file_text(file_index: 'FileIndex') -> str:
        """
        Generate embedding text for a file.
        
        Format: "File <filename> containing <up to 3 class names>"
        
        Args:
            file_index: The FileIndex object
            
        Returns:
            Short embedding text for the file
        """
        filename = os.path.basename(file_index.file_path)
        
        if not file_index.members:
            return f"File {filename}"
        
        # Get up to 3 class names
        class_names = [member.name for member in file_index.members[:3]]
        classes_str = ", ".join(class_names)
        
        return f"File {filename} containing {classes_str}"

    @staticmethod
    def member_text(member: 'CodeMember') -> str:
        """
        Generate embedding text for a member (class/interface/enum).
        
        Format: "<ClassName> <class|interface|enum> - <first sentence of summary>"
        
        Args:
            member: The CodeMember object
            
        Returns:
            Short embedding text for the member
        """
        member_type = member.type.value
        
        # Extract first sentence from summary
        first_sentence = EmbeddingStrategy._get_first_sentence(member.summary)
        
        if first_sentence:
            return f"{member.name} {member_type} - {first_sentence}"
        else:
            return f"{member.name} {member_type}"

    @staticmethod
    def method_text(method: 'CodeMethod', member_name: str) -> str:
        """
        Generate embedding text for a method.
        
        Format: "<methodName> method in <ClassName> - <first sentence of summary>"
        
        Args:
            method: The CodeMethod object
            member_name: The name of the containing class/interface
            
        Returns:
            Short embedding text for the method
        """
        # Extract first sentence from summary
        first_sentence = EmbeddingStrategy._get_first_sentence(method.summary)
        
        if first_sentence:
            return f"{method.name} method in {member_name} - {first_sentence}"
        else:
            return f"{method.name} method in {member_name}"

    @staticmethod
    def _get_first_sentence(text: str) -> str:
        """
        Extract the first sentence from text.
        
        Args:
            text: The text to extract from
            
        Returns:
            The first sentence, or empty string if no text
        """
        if not text:
            return ""
        
        text = text.strip()
        
        # Find first sentence ending with period, question mark, or exclamation
        for delimiter in ['. ', '? ', '! ']:
            if delimiter in text:
                return text.split(delimiter)[0] + delimiter.strip()
        
        # If no sentence delimiter found, return the whole text
        return text
