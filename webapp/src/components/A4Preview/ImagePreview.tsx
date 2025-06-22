import { useState, useEffect } from 'react';
import A4Container from './A4Container';
import LoadingSpinner from '../Common/LoadingSpinner';
import type { PatientStudy } from '../../types/dicom.types';
import { orthancApiService } from '../../services/orthancApi';

interface ImagePreviewProps {
  patientStudy: PatientStudy;
  scale?: 'desktop' | 'tablet' | 'mobile' | 'print';
  className?: string;
  maxImages?: number;
}

interface DicomImage {
  id: string;
  url: string;
  description?: string;
  seriesDescription?: string;
  instanceNumber?: number;
  isLoading?: boolean;
  hasError?: boolean;
}

export default function ImagePreview({ 
  patientStudy, 
  scale = 'desktop',
  className = '',
  maxImages = 8
}: ImagePreviewProps) {
  const [images, setImages] = useState<DicomImage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDicomImages();
  }, [patientStudy.id]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadDicomImages = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Extract study ID from patient study ID
      const studyId = patientStudy.id.split('-')[1] || patientStudy.id;
      
      // Get study details to find series
      const study = await orthancApiService.getStudy(studyId);
      
      const imagePromises: Promise<DicomImage>[] = [];
      let imageCount = 0;

      // Process each series up to maxImages
      for (const seriesId of study.Series) {
        if (imageCount >= maxImages) break;

        try {
          const series = await orthancApiService.getSeries(seriesId);
          
          // Take first few instances from each series
          const instancesToTake = Math.min(
            series.Instances.length, 
            maxImages - imageCount
          );

          for (let i = 0; i < instancesToTake; i++) {
            const instanceId = series.Instances[i];
            
            imagePromises.push(
              createDicomImage(instanceId, series.SeriesDescription, i + 1)
            );
            imageCount++;
          }
        } catch {
          console.warn(`Error loading series ${seriesId}`);
        }
      }

      // Wait for all images to be processed
      const loadedImages = await Promise.allSettled(imagePromises);
      
      const validImages = loadedImages
        .filter((result): result is PromiseFulfilledResult<DicomImage> => 
          result.status === 'fulfilled'
        )
        .map(result => result.value);

      // Fill remaining slots with placeholders if needed
      const remainingSlots = maxImages - validImages.length;
      const placeholders = Array.from({ length: remainingSlots }, (_, index) => ({
        id: `placeholder-${index}`,
        url: '',
        description: 'No image available',
        isLoading: false,
        hasError: false,
      }));

      setImages([...validImages, ...placeholders]);
    } catch (error) {
      console.error('Error loading DICOM images:', error);
      setError(error instanceof Error ? error.message : 'Failed to load images');
      
      // Create placeholder images
      const placeholders = Array.from({ length: maxImages }, (_, index) => ({
        id: `error-placeholder-${index}`,
        url: '',
        description: 'Failed to load',
        isLoading: false,
        hasError: true,
      }));
      
      setImages(placeholders);
    } finally {
      setIsLoading(false);
    }
  };

  const createDicomImage = async (
    instanceId: string, 
    seriesDescription?: string, 
    instanceNumber?: number
  ): Promise<DicomImage> => {
    try {
      // For now, we'll use a placeholder since we need the actual Orthanc preview endpoint
      // In a real implementation, this would be: `/instances/${instanceId}/preview`
      const previewUrl = `${import.meta.env.REACT_APP_ORTHANC_URL || 'http://localhost:8042'}/instances/${instanceId}/preview`;
      
      return {
        id: instanceId,
        url: previewUrl,
        description: `Instance ${instanceNumber}`,
        seriesDescription,
        instanceNumber,
        isLoading: false,
        hasError: false,
      };
    } catch {
      return {
        id: instanceId,
        url: '',
        description: `Instance ${instanceNumber} (Error)`,
        seriesDescription,
        instanceNumber,
        isLoading: false,
        hasError: true,
      };
    }
  };

  const handleImageError = (imageId: string) => {
    setImages(prevImages =>
      prevImages.map(img =>
        img.id === imageId ? { ...img, hasError: true } : img
      )
    );
  };

  const handleImageLoad = (imageId: string) => {
    setImages(prevImages =>
      prevImages.map(img =>
        img.id === imageId ? { ...img, isLoading: false } : img
      )
    );
  };

  if (isLoading) {
    return (
      <A4Container scale={scale} className={className}>
        <div className="flex items-center justify-center h-full">
          <LoadingSpinner size="lg" message="Loading DICOM images..." />
        </div>
      </A4Container>
    );
  }

  if (error) {
    return (
      <A4Container scale={scale} className={className}>
        <div className="flex flex-col items-center justify-center h-full text-center">
          <div className="w-16 h-16 mb-4 text-red-400">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-full h-full">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="text-lg font-bold mb-2">Failed to Load Images</h3>
          <p className="text-sm text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadDicomImages}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            Retry
          </button>
        </div>
      </A4Container>
    );
  }

  return (
    <A4Container scale={scale} className={className}>
      <div className="h-full">
        <div className="mb-4 pb-2 border-b-2 border-gray-400">
          <h2 className="text-lg font-bold text-center">IMAGENS DICOM</h2>
          <p className="text-sm text-center text-gray-600">
            {patientStudy.patientName} - {patientStudy.studyDescription}
          </p>
        </div>
        
        <div className="a4-image-grid">
          {images.map((image) => (
            <div key={image.id} className="a4-image-item">
              {image.url && !image.hasError ? (
                <>
                  <img
                    src={image.url}
                    alt={image.description}
                    onLoad={() => handleImageLoad(image.id)}
                    onError={() => handleImageError(image.id)}
                    className="max-w-full max-h-full object-contain"
                  />
                  <div className="a4-image-caption">
                    {image.seriesDescription || image.description}
                  </div>
                </>
              ) : (
                <div className="flex flex-col items-center justify-center text-gray-500 text-center">
                  <svg className="w-8 h-8 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span className="text-xs">
                    {image.hasError ? 'Failed to load' : image.description}
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
        
        <div className="mt-4 pt-2 border-t border-gray-400 text-xs text-center">
          <p>
            Showing {images.filter(img => img.url && !img.hasError).length} of {patientStudy.instanceCount} total images
          </p>
        </div>
      </div>
    </A4Container>
  );
}